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
