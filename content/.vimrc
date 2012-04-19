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

inoremap <F6> <C-R>=strftime("* %a %b %d %Y Ralph Bean <rbean@redhat.com> ")<CR>

" Shortcut to rapidly toggle `set paste`    CONTROL-P
nmap <C-p> :set paste!<CR>

" Shortcut to rapidly toggle `set list`     CONTROL-L
nmap <C-l> :set list!<CR>

" Use the same symbols as TextMate for tabstops and EOLs
"set listchars=tab:▸\ ,eol:¬

highlight OverLength ctermbg=red ctermfg=white guibg=#592929
match OverLength /\%81v.\+/
