call pathogen#infect()
set expandtab
set tabstop=4
set shiftwidth=4
set smartindent
set noeb vb t_vb=
set laststatus=2

" Email coloration in sup
au BufRead sup.*        set ft=mail

:filetype on

:filetype indent on

let g:js_indent_log = 0
set textwidth=80

set background=dark
let g:solarized_termcolors=16
colorscheme solarized
" colorscheme vividchalk

highlight BadWhitespace ctermbg=red guibg=red
au BufRead,BufNewFile *.rst match BadWhitespace /*\t\*/
au BufRead,BufNewFile *.rst match BadWhitespace /\s\+$/
au BufRead,BufNewFile *.py match BadWhitespace /*\t\*/
au BufRead,BufNewFile *.py match BadWhitespace /\s\+$/

au BufNewFile,BufRead *.mak set ft=mako

highlight OverLength ctermbg=red ctermfg=white guibg=#592929
match OverLength /\%81v.\+/
