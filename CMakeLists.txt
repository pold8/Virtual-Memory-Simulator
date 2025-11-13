cmake_minimum_required(VERSION 3.30)
project(VMSimulator)

set(CMAKE_CXX_STANDARD 20)

add_executable(VMSimulator main.cpp
        frame.cpp
        memory.cpp
        page_table.cpp
        mmu.cpp)
