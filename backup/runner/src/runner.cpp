#include <exception>
#include <expected>
#include <fstream>
#include <filesystem>
#include <optional>
#include <utility>
#include <memory>
#include <variant>

#include <spdlog/spdlog.h>
#include <mw/error.hpp>
#include <mw/utils.hpp>
#include <mw/exec.hpp>

#include "runner.hpp"

namespace {

template<typename T>
using E = mw::E<T>;

E<std::vector<char>> readFile(const std::filesystem::path& path)
{
    std::ifstream f(path, std::ios::binary);
    std::vector<char> content;
    content.reserve(102400);
    content.assign(std::istreambuf_iterator<char>(f),
                   std::istreambuf_iterator<char>());
    if(f.bad() || f.fail())
    {
        return std::unexpected(mw::runtimeError(
            std::format("Failed to read file {}", path.string())));
    }
    return content;
}

E<void> doBackup(const std::string& path,
                 const std::optional<std::string>& profile,
                 bool dry_run)
{
    std::vector<const char*> argv = {"rustic",};
    if(dry_run)
    {
        argv.push_back("--dry-run");
    }
    if(profile.has_value())
    {
        argv.push_back("--use-profile");
        argv.push_back(profile->c_str());
    }
    argv.push_back(path.c_str());
    ASSIGN_OR_RETURN(mw::Process proc,
                     mw::Process::exec(nullptr, argv, nullptr));
    ASSIGN_OR_RETURN(int code, proc.wait());
    if(code != 0)
    {
        return std::unexpected(mw::runtimeError(
            std::format("Rustic failed with code {}", code)));
    }
    return {};
}

E<void> doBackup(const StdoutBackup& stdout_spec,
                 const std::optional<std::string>& profile,
                 bool dry_run)
{
    std::string additional_rustic_opts;
    if(profile.has_value())
    {
        additional_rustic_opts = "--use-profile ";
        additional_rustic_opts += *profile;
    }
    std::string command = std::format(
        "set -euo pipefail; {} | rustic --stdin-filename {} {} -",
        stdout_spec.command, stdout_spec.filename, additional_rustic_opts);

    if(dry_run)
    {
        spdlog::info("Dry run: {} {}", "bash -c", command);
        return {};
    }

    ASSIGN_OR_RETURN(mw::Process proc,
                     mw::Process::exec(nullptr, {"bash", "-c", command.c_str()}, nullptr));
    ASSIGN_OR_RETURN(int code, proc.wait());
    if(code != 0)
    {
        return std::unexpected(mw::runtimeError(
            std::format("Rustic pipe failed with code {}", code)));
    }
    return {};
}

} // namespace

E<BackupSpec> BackupSpec::fromYaml(c4::yml::ConstNodeRef yaml_node)
{
    BackupSpec spec;
    if(!yaml_node["source"].readable())
    {
        return std::unexpected(mw::runtimeError("Backup source not specified"));
    }
    auto source_node = yaml_node["source"];

    if(!source_node["type"].readable())
    {
        return std::unexpected(mw::runtimeError("Source type not specified"));
    }
    if(source_node["type"].val() == "path")
    {
        if(!source_node["path"].readable())
        {
            return std::unexpected(mw::runtimeError("Source path not specified"));
        }
        std::string path;
        source_node["path"] >> path;
        spec.source = std::move(path);
    }
    else if(source_node["type"].val() == "output")
    {
        if(!source_node["command"].readable())
        {
            return std::unexpected(mw::runtimeError(
                "Source command not specified"));
        }
        if(!source_node["output-path"].readable())
        {
            return std::unexpected(mw::runtimeError(
                "Source output path not specified"));
        }
        StdoutBackup out;
        source_node["command"] >> out.command;
        source_node["output-path"] >> out.filename;
        spec.source = std::move(out);
    }

    if(yaml_node["rustic-profile"].readable())
    {
        std::string profile;
        yaml_node["rustic-profile"] >> profile;
        spec.rustic_profile = std::move(profile);
    }

    return spec;
}

mw::E<BackupPlan> BackupPlan::fromYaml(std::string_view filename)
{
    auto buffer = readFile(filename);
    if(!buffer.has_value())
    {
        return std::unexpected(buffer.error());
    }

    ryml::Tree tree = ryml::parse_in_place(ryml::to_substr(*buffer));

    if(!tree["sources"].readable())
    {
        return std::unexpected(mw::runtimeError("Sources not specifed"));
    }
    if(!tree["sources"].is_seq())
    {
        return std::unexpected(mw::runtimeError("Sources should be a list"));
    }

    BackupPlan plan;
    if(tree["rustic-profile"].readable())
    {
        std::string profile;
        tree["rustic-profile"] >> profile;
        plan.rustic_profile = std::move(profile);
    }
    for(const auto& source: tree["sources"])
    {
        ASSIGN_OR_RETURN(BackupSpec spec, BackupSpec::fromYaml(source));
        plan.specs.push_back(std::move(spec));
    }
    return plan;
}

E<void> runBackup(const BackupPlan& plan, bool dry_run)
{
    const std::optional<std::string>* profile = &plan.rustic_profile;

    for(const BackupSpec& spec: plan.specs)
    {
        if(spec.rustic_profile.has_value())
        {
            profile = &spec.rustic_profile;
        }
        if(std::holds_alternative<std::string>(spec.source))
        {
            const std::string& path = std::get<std::string>(spec.source);
            auto result = doBackup(path, *profile, dry_run);
            if(!result.has_value())
            {
                spdlog::error("Failed to backup {}: {}", path,
                              mw::errorMsg(result.error()));
            }
        }
        else if(std::holds_alternative<StdoutBackup>(spec.source))
        {
            const StdoutBackup& back = std::get<StdoutBackup>(spec.source);
            auto result = doBackup(back, *profile, dry_run);
            if(!result.has_value())
            {
                spdlog::error("Failed to backup {}: {}", back.filename,
                              mw::errorMsg(result.error()));
            }
        }
        else
        {
            std::unreachable();
        }
    }
    return {};
}
