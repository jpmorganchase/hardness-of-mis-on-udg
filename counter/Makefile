CC=g++
CFLAGS=-O3 -fomit-frame-pointer -std=c++11

gs_counter: gs_counter.cc
	$(CC) -o $@ $^ $(CFLAGS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o

