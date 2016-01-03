#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include </usr/include/linux/hdreg.h>
#include "openssl/ssl.h"

/*
 * Depending on your system and installed packages
 * you might need libcurl4-openssl-dev
 */

static int open_flags = O_RDONLY|O_NONBLOCK;

//conglomerate function deduced from an aggregate of hdparm functions
static char* get_serial(char* b_device)
{
    //extract the block devices serial
    __u16 id2[256];
    int err = 0;
    int fd;

    fd = open(b_device, open_flags);

    if (fd < 0)
    {
        err = errno;
        perror(b_device);
        exit(err);
    }

    if (!ioctl(fd, HDIO_GET_IDENTITY, id2))
    {
        /*
         * Assumming that the device doesn't have multcount enabled...
         * HDIO_GET_MULTCOUNT, if rolled out this should be checked...
         */

        id2[59] &= ~0x100;

        return strndup((char *)&id2[10], 20);

    } else if (errno == -ENOMSG) {
        printf(" no identification info available\n");
    } else {
        err = errno;
        perror(" HDIO_GET_IDENTITY failed");
    }

    return NULL;
}

static char* get_fingerprint(char* b_device, char* serial)
{
    //There should be something unique in the first 512 bytes of each drive
    //we are going to rip and hash that after concatenating it to the serial
    int fd,err;
    fd = open(b_device, open_flags);

    if (fd < 0)
    {
        err = errno;
        perror(b_device);
        exit(err);
    }
    //pull in the partition table and hash it...
    int slen = strlen(serial); // perhaps use strnlen if this is an issue...
    SHA_CTX s;
    int SIZE = 512;
    int ret, cnt, i;
    cnt = SIZE;
    char b;
    char c[SIZE+slen];
    memset(c, '\0', SIZE+slen);
    strncat(serial, c, slen);
    unsigned char hash[20];

    SHA1_Init(&s);
    while((ret = read (fd, &b, 1)) > 0 && cnt > 0){
        c[cnt] = b;
        cnt -= ret;
    }
    SHA1_Update(&s, c, SIZE);
    SHA1_Final(hash, &s);

    char mhash[42];
    cnt = 0;
    for(i=0;i<20;i++){
        cnt+=snprintf ( mhash+cnt, 3, "%.2x", (int)hash[i]);
    }
    return strdup(mhash);//safe b/c snprintf places the null terminator.
}

int main(int argc, char** argv)
{
    if(argc < 2)
    {
        puts("You need to supply me with a block device location\nExample: /dev/sda");
        exit(-1);
    }
    //should use getopt but it's quick code...
    char* device = argv[1];// perhaps an issue, leaving for now since only example code
    char* serial = get_serial(device);// add checking later if desired

    char *fingerprint = get_fingerprint(device, serial);

    printf("\nDevice:%s\nSerial:%s\nFingerprint:%s\n", device, serial, fingerprint);

    free(serial);
    free(fingerprint);

    return 0;
}
