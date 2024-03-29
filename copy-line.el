;; This file is NOT part of GNU Emacs.
;;
;; This program is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.
;;
;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.
;;
;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.
;;
;; author: Marco Chieppa | crap0101
;;

(defun copy-lines (&optional arg)
  "Copy *arg* lines in the kill ring (default: the current line)."
  (interactive "p")
  (kill-ring-save (line-beginning-position)
		  (line-beginning-position (+ 1 (if arg arg 1)))))

;;(global-set-key "\C-c\C-c" 'copy-lines)

;; C-c C-c for copy the current line
;; C-u N C-c C-c to copy N lines
