#include <iostream>

#include <cxxopts.hpp>
#include <spdlog/spdlog.h>

#include "mw/error.hpp"
#include "runner.hpp"

int main(int argc, char** argv)
{
    cxxopts::Options cmd_options(
        "Backup runner", "A naively simple Rustic caller");
    cmd_options.add_options()
        ("p,plan", "Backup plan file",
         cxxopts::value<std::string>()->default_value("/etc/backup.yaml"))
        ("n,dry-run", "Dry run")
        ("h,help", "Print this message.");
    auto opts = cmd_options.parse(argc, argv);

    if(opts.count("help"))
    {
        std::cout << cmd_options.help() << std::endl;
        return 0;
    }

    const std::string plan_file = opts["plan"].as<std::string>();
    auto plan = BackupPlan::fromYaml(std::move(plan_file));
    if(!plan.has_value())
    {
        spdlog::error("Failed to load backup plan: {}",
                      mw::errorMsg(plan.error()));
        return 1;
    }

    const bool dry_run = opts.count("dry-run") > 0;
    mw::E<void> result = runBackup(*plan, dry_run);
    if(!result.has_value())
    {
        spdlog::error("Failed to backup: {}", mw::errorMsg(result.error()));
        return 1;
    }
    return 0;
}
