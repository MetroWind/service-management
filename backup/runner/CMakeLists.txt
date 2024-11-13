# cmake -B build . && cmake --build build -j
cmake_minimum_required(VERSION 3.24)

set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

project(BackupRunner)

include(FetchContent)
FetchContent_Declare(
  libmw
  GIT_REPOSITORY https://github.com/MetroWind/libmw.git
)

FetchContent_Declare(
  cxxopts
  GIT_REPOSITORY https://github.com/jarro2783/cxxopts.git
  GIT_TAG v3.1.1
)

FetchContent_Declare(
  ryml
  GIT_REPOSITORY https://github.com/biojppm/rapidyaml.git
  GIT_TAG
  GIT_SHALLOW FALSE  # ensure submodules are checked out
)

FetchContent_Declare(
  spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG v1.12.0
)

set(SPDLOG_USE_STD_FORMAT ON)
FetchContent_MakeAvailable(libmw ryml spdlog cxxopts)

set(SOURCE_FILES
  src/main.cpp
  src/runner.hpp
  src/runner.cpp
)

set(LIBS
  cxxopts
  spdlog::spdlog
  ryml::ryml
  mw
)

set(INCLUDES
  ${libmw_SOURCE_DIR}/includes
)

add_executable(backup-runner ${SOURCE_FILES} src/main.cpp)
set_property(TARGET backup-runner PROPERTY CXX_STANDARD 23)

set_property(TARGET backup-runner PROPERTY COMPILE_WARNING_AS_ERROR TRUE)
target_compile_options(backup-runner PRIVATE -Wall -Wextra -Wpedantic)
target_include_directories(backup-runner PRIVATE ${INCLUDES})
target_link_libraries(backup-runner PRIVATE ${LIBS})
