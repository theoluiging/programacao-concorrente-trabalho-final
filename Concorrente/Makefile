CC = gcc
CFLAGS = -Wall -O3 -pthread
TARGET = amdc

all: $(TARGET)

$(TARGET): amdc.c
	$(CC) $(CFLAGS) -o $(TARGET) amdc.c

debug: CFLAGS += -DDEBUG -g
debug: $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all debug clean
