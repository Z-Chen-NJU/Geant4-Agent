cmake_minimum_required(VERSION 3.16)
project(geant4_local_app LANGUAGES CXX)

find_package(Geant4 11.4 REQUIRED ui_win32 vis_opengl_win32)

add_executable(geant4_local_app main.cc)
target_link_libraries(geant4_local_app PRIVATE ${Geant4_LIBRARIES})
target_include_directories(geant4_local_app PRIVATE ${Geant4_INCLUDE_DIRS})
target_compile_features(geant4_local_app PRIVATE cxx_std_17)
