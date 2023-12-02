;; .emacs init file by Marco Chieppa | crap0101


;; load vibuf ;;
(add-to-list 'load-path "/home/crap0101/local/share/emacs")
(require 'vibuf)
; add hooks
(add-hook 'find-file-hook 'vibuf-create-buffer-hook-function)
(add-hook 'kill-buffer-hook 'vibuf-kill-buffer-hook-function)
(add-hook 'emacs-startup-hook 'vibuf-set__buffer-list-default)
(add-hook 'emacs-startup-hook (lambda () (vibuf-set__excluded-names vibuf__excluded-names)))
; set some vars
(vibuf-set__buffer-name-if-empty "*scratch*")
; ...and set key bindings
(global-set-key (kbd "C-S-<left>") (lambda () (interactive) (vibuf-prev-buffer)))
(global-set-key (kbd "C-S-<right>") (lambda () (interactive) (vibuf-next-buffer)))





;; maximize window
(setq initial-frame-alist '((fullscreen . maximized)))

;; set & start emacs server
(require 'server)
;;(setq server-name "emacs-server-main")
(unless (server-running-p)
  (server-start)
  (message (format "server started (%s)" (server-running-p))))


;;;;;;;;;;;;;;;;;;;;;;
;; custom functions ;;
;;;;;;;;;;;;;;;;;;;;;;

; custom goto-line
(defun go-line (num)
  "go to the *num*th line of the current buffer.
NOTE: If *num* is lesser than 1 or negative, counts from the
end of the buffer; else if greater than the number of
buffer's lines, go to the last line."
  (interactive "NGo to line: ")
  (push-mark)
  (let ((actual-line (line-number-at-pos)))
    (let ((lines (line-number-at-pos (point-max))))
      (if (> num lines)
          (forward-line (- lines actual-line))
        (if (<= num 0)
            (forward-line (+ (- lines actual-line) num))
          (forward-line (- num actual-line)))))))

; copy-line shortcut
(defun copy-lines (&optional arg)
  "Copy *arg* lines in the kill ring (default: the current line)."
  (interactive "p")
  (kill-ring-save (line-beginning-position)
		  (line-beginning-position (+ 1 (if arg arg 1)))))

; search by region
(defun search-region (start end)
  "Starts a search using the region of the current buffer."
  (interactive "r")  
  (isearch-mode t nil nil nil)
  (deactivate-mark)
  (isearch-yank-string (buffer-substring-no-properties start end)))

; insert date
(defun insert-date (prefix)
    "Insert the current date."
    (interactive "P")
    (insert (format-time-string "%Y-%m-%d")))

; run python program
(defun run-python-program (&optional python-name)
  "Run the python programs in the current buffer"
  (interactive)
  (let ((pyv (if python-name python-name "python")))
    (if (string= (save-excursion (current-buffer) major-mode) "python-mode")
	(progn (message
		(concat "Running " pyv  " script "
			(car (reverse (split-string (buffer-name) "/")))))
	       (shell-command
		(concat "/usr/bin/env " pyv " " (buffer-file-name))))
      (message (concat
		"Error: This not seem a python file. Nothing executed. ("
		(symbol-name
		 (save-excursion (current-buffer) major-mode)) ")")))))

; run python program (choose executable)
(defun run-pythonXY-program (python-name)
  (interactive "sPython name: ")
  (run-python-program python-name))

; number to subscript (O2 -> O₂)
(defun number-to-subscript ()
  (let* ((cursor-info (what-cursor-position))
	 (ival (progn (string-match "(\\([0-9]+\\)" cursor-info)
		      (string-to-number (match-string 1 cursor-info)))))
    (if (and (>= ival 48) (<= ival 57))
	(progn
	  (delete-char 1)
	  (insert (format "%c" (+ 8272 ival)))))))


;;;;;;;;;;;;;;
;; bindings ;;
;;;;;;;;;;;;;;

;; redefine this
(global-set-key "\C-xw" 'other-window)

;; others simple bindings
(global-set-key "\C-c\C-r" (lambda () (interactive)
			     (progn (revert-buffer nil t) (message "%s" "buffer reverted"))))
;; for previously defined functions
(global-set-key "\C-cg" 'go-line)
(global-set-key "\C-c\C-c" 'copy-lines)
(global-set-key (kbd "C-S-s") 'search-region)
(global-set-key (kbd "C-c d") 'insert-date)
(global-set-key (kbd "M-s") (lambda () (interactive) (number-to-subscript)))
(global-set-key [f2] 'run-python-program)
(global-set-key [f3] 'run-pythonXY-program)
; change font size with C-[MouseWheelUpOrDown]
(global-set-key (kbd "<C-mouse-4>") (lambda () (interactive) (text-scale-decrease 1)))
(global-set-key (kbd "<C-mouse-5>") (lambda () (interactive) (text-scale-increase 1)))


;;;;;;;;;;;;;;;;;;;;;;
;; custom variables ;;
;;;;;;;;;;;;;;;;;;;;;;

; http://lists.gnu.org/archive/html/emacs-devel/2011-09/msg00350.html
(setq redisplay-dont-pause t)
;; https://lists.gnu.org/archive/html/bug-gnu-emacs/2010-11/msg00243.html
(setq focus-follows-mouse nil)
; keep the cursor at the same screen position whenever a scroll command moves it off-window
(setq scroll-preserve-screen-position t)
; browser
(setq browse-url-browser-function 'browse-url-firefox
      browse-url-firefox-program "firefox")
; no beep
(setq visible-bell t)
; text related
(setq indent-tabs-mode nil
      tab-width 4
      term-input-autoexpand t
      x-select-enable-clipboard t)
; columns and rows
(line-number-mode t)
(column-number-mode t)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; set color, faces and similar stuffs ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; (set-background-color "#000000") ;"#333333")
; (set-foreground-color "#33CC00")
(set-face-attribute 'default t
                    :stipple nil
                    :inverse-video nil
                    :box nil
                    :strike-through nil
                    :overline nil
                    :underline nil
                    :slant 'normal
                    :weight 'normal
                    :height 120
                    :width 'normal
                    :family "DejaVu Sans Mono")
(set-face-attribute 'region nil :background "#666666")
(set-frame-font "DejaVu Sans Mono 15")


;; erc ;;
;(require 'erc-join)
;(erc-autojoin-mode 1)
(setq erc-modules '(autojoin button completion dcc fill irccontrols
                             list match menu move-to-prompt netsplit
                             networks noncommands readonly ring stamp track)
      erc-autojoin-channels-alist '(("freenode.net" "#hackerforum" "#init1" "#linux-libre"))
      erc-away-nickname nil
      erc-prompt-for-channel-key nil
      erc-public-away-p nil
      erc-user-full-name "Marco Chieppa | http://crap0101.altervista.org/"
      erc-auto-discard-away t
      erc-autoaway-idle-seconds 900)

;; rust ;;
(add-to-list 'load-path "/home/crap0101/.emacs.d/rust")
(require 'rust-mode)
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
