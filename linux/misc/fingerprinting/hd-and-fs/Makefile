
CC=gcc
CFLAGS=-I. -Wall -ggdb -lssl
DEPS = 

NAME = $(target)

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

all: $(NAME).o
	$(CC) -o $(NAME) $(NAME).o $(CFLAGS)

clean:
	rm -rf *~ *o $(NAME)
