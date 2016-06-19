;; number to subscript (O2 -> O₂)
(defun number-to-subscript ()
  (let* ((cursor-info (what-cursor-position))
     (ival (progn (string-match "(\\([0-9]+\\)" cursor-info)
              (string-to-number (match-string 1 cursor-info)))))
    (if (and (>= ival 48) (<= ival 57))
    (progn
      (delete-char 1)
      (insert (format "%c" (+ 8272 ival)))))))


;; bind with:
;; (global-set-key (kbd "M-s") (lambda () (interactive) (number-to-subscript)))
