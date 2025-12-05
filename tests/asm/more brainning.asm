; single_file.asm

global main
global function

section .data
    msg db "hello world!", 0

section .text

; ---------------------------------------------------------
; int function(char* string)
; ---------------------------------------------------------
function:
    push rbp
    mov  rbp, rsp

    mov  rax, rdi        ; string pointer
    xor  ecx, ecx        ; index = 0

.len_loop:
    cmp  byte ptr [rax + rcx], 0
    je   .done
    inc  ecx
    jmp  .len_loop

.done:
    mov  eax, ecx        ; return index
    pop  rbp
    ret


; ---------------------------------------------------------
; int main()
; ---------------------------------------------------------
main:
    push rbp
    mov  rbp, rsp

    lea  rdi, [rel msg]  ; argument: "hello world!"
    call function        ; ignore return value, same as your C code

    mov  eax, 0          ; return 0
    leave
    ret
