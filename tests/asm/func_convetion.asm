section .text
global _start

functionTest:
    pop rax
    pop rbx
    add rax, rbx
    ret

_start:
    jmp main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16 ; prologue

    call functionTest

    push 1
    push 2 

    add rsp, 16 ; epilogue