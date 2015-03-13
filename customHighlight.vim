function! customHighlight#Initiate()
	let g:highlightedBool = 1
        nnoremap <F5> :call customHighlight#HighlightMyText()<CR>
endfunction

function! customHighlight#HighlightMyText(...)
	if g:highlightedBool == 1
		hi gr1 ctermbg=red ctermfg=0
		match gr1 /NOTE/
		2match gr1 /BUG/
		let g:highlightedBool = 0
	else
		hi clear gr1
		let g:highlightedBool = 1
	endif
endfunction
