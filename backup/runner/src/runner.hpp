#pragma once

#include <string>
#include <vector>
#include <optional>
#include <variant>
#include <string_view>

#include <ryml.hpp>
#include <ryml_std.hpp>
#include <c4/yml/node.hpp>

#include "mw/error.hpp"

struct StdoutBackup
{
    std::string command;
    std::string filename;
};

struct BackupSpec
{
    std::optional<std::string> rustic_profile;
    std::variant<std::string, StdoutBackup> source;

    static mw::E<BackupSpec> fromYaml(c4::yml::ConstNodeRef yaml_node);
};

struct BackupPlan
{
    std::optional<std::string> rustic_profile;
    std::vector<BackupSpec> specs;
    static mw::E<BackupPlan> fromYaml(std::string_view filename);
};

mw::E<void> runBackup(const BackupPlan& plan, bool dry_run);
