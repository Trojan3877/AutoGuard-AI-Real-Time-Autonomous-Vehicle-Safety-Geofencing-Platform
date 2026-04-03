cmake_minimum_required(VERSION 3.18)
project(autoguard_risk_engine VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization flags for release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    add_compile_options(-O3 -march=native)
endif()

# Shared library for Python binding via ctypes / cffi
add_library(risk_engine SHARED risk_engine.cpp)

target_include_directories(risk_engine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Strip symbols in release to reduce binary size
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    add_custom_command(TARGET risk_engine POST_BUILD
        COMMAND ${CMAKE_STRIP} $<TARGET_FILE:risk_engine>)
endif()

# Installation
install(TARGETS risk_engine DESTINATION lib)
install(FILES risk_engine.h DESTINATION include OPTIONAL)

# ── Optional: standalone test binary ─────────────────────────────────────────
option(BUILD_TESTS "Build the standalone risk_engine test binary" OFF)
if(BUILD_TESTS)
    add_executable(risk_engine_test risk_engine_test.cpp)
    target_link_libraries(risk_engine_test PRIVATE risk_engine)
endif()
