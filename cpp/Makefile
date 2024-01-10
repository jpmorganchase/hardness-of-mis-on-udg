######################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
######################################################################

CC     = g++
CPPFLAGS = -DNDEBUG -O3 -fomit-frame-pointer -std=c++11

default: fixed_depth_sa sweeping_line

fixed_depth: fixed_depth_sa.cc
	$(CC) $(CPPFLAGS) -o $@ $^ 

sweeping_line: sweeping_line.cc
	$(CC) $(CPPFLAGS) -o $@ $^ 