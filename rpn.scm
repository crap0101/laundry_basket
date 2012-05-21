;; Reverse Polish notation (RPN) calulator.

; Copyright (C) 2011  Marco Chieppa (aka crap0101)

; Permission is hereby granted, free of charge, to any person obtaining a copy
; of this software and associated documentation files (the "Software"), to
; deal in the Software without restriction, including without limitation the
; rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
; sell copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:

; The above copyright notice and this permission notice shall be included in
; all copies or substantial portions of the Software.

; THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
; IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
; MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
; IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
; SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
; PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
; WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
; OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
; ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


(define rpn
  (lambda (str)
    (letrec ((string (open-input-string str))
             (numlist '())
             (push (lambda (n)
                     (set! numlist (append (list n) numlist))))
             (pop (lambda ()
                    (let ((snd (car numlist))
                          (fst (car (cdr numlist))))
                      (set! numlist (cdr (cdr numlist)))
                      (list fst snd))))
             (loop (lambda ()
                     (let ((next (read string)))
                       (if (eof-object? next)
                           (if (> (length numlist) 1) "malformed expression"
                               (car numlist))
                           (begin
                             (cond ((number? next) (push next))
                                   ((eq? next '+) (push (apply + (pop))))
                                   ((eq? next '-) (push (apply - (pop))))
                                   ((eq? next '*) (push (apply * (pop))))
                                   ((eq? next '/) (push (exact->inexact (apply / (pop)))))
                                   ((eq? next '%) (push (apply modulo (pop))))
                                   ((eq? next '^) (push (apply expt (pop)))))
                             (loop)))))))
      (loop))))



;; examples
;; > (rpn "5 1 2 + 4 * + 3 -")
;; 14
;; > (rpn "1 2 + 4 5 * -")
;; -17
;; > (rpn "1 2 3 + 4 5 * -")
;; "malformed expression"
;; > (rpn "1 7 3 / 1 4 - 2 * / +")
;; 0.6111111111111112
;; > (rpn "10 2 * 4 5 - + 2 /")
;; 9.5
