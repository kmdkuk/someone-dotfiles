# yourdotfiles

みんなの dotfiles

## [lewagon/dotfiles](https://github.com/lewagon/dotfiles)

Lewagon というオンラインの学校の生徒向けらしい。
みんなに配る向けなだけあって、git,zsh,ruby,ssh,vscode の設定を symlink で配置するだけのシンプルなものになっている。

## [thoughtbot/dotfiles](https://github.com/thoughtbot/dotfiles)

rcm(rc manager)を使っている。
頭に.なしのものを用意しておいておくと、rcm が.をつけてホームに symlink を作ってくれるらしい。
README の説明が丁寧
zsh 使い

## [holman/dotfiles](https://github.com/holman/dotfiles)

ディレクトリ分けがきれいにされている。
ROOT にあるのは Brewfile のみ。
symlink を作りたいものは vimrc.symlink のようにしておいて、
installscript から.symlink を find して、ホームディレクトリに symlink を作っていくらしい。
基本.zsh といった、zsh で読み込ませるスクリプトが多め。たぶん mac 使いの方。
macos/ の script は、自分も参考にしたい。
`export ZSH=$HOME/.dotfiles`として、symlink を貼っていないものに関しては、直接 path 指定で source しているっぽい

## [craftzdog/dotfiles-public](https://github.com/craftzdog/dotfiles-public)

README 見たら youtube で見たことある方だ。NeoVim で React か ReactNative をカタカタしている動画を見た記憶がある。
それぞれの config で何を使っているか説明されていてとても良い。
public と書いているだけあって、インストールスクリプトがあってバチッと setup できるものではなさそう。
config 集といった感じ。
fish 使い

## [mathiabynens/dotfiles](https://github.com/mathiasbynens/dotfiles)

symlink ではなく rsync で配置。rsync よくわかっていないけど、更新するときは再度 bootstrap.sh を実行するのかな？
macos の defaults コマンドをこちらの方もかなり整備している。
bash 使い
.config XDG config path は使っていなさそう。すべて home に配置するもので構成されている。

## [jessfraz/dotfiles](https://github.com/jessfraz/dotfiles)

Makefile で bootstrap する。
shellcheck を実行する test target も用意されている。
Linux 使いで、etc 下の設定も管理されている。
たぶん bash 使い
bootstrap のときに`git update-index--skip-worktree'を使って、追跡から外している。多分これで private な設定を入れたりしてるのだろう。

## [driesvints/dotfiles](https://github.com/driesvints/dotfiles)

oh-my-zsh で Mac 用。
brew 以外にも macup というツールを使っている。
laravel をよく使っている方のようで、関連リポジトリを clone するスクリプトや、DB に関するスクリプトが含まれている。

## [CoreyMSchafer/dotfiles](https://github.com/CoreyMSchafer/dotfiles)

Mac 用。
Bash も Zsh も両方の設定を含んでいる。
あとは、brew, sublime, vscode の設定あたり。
sublime テキストを見て懐かしくなった。
brew は bundle を利用せず、brew.sh に直接パッケージ名を記載している。

## [cowboy/dotfiles](https://github.com/cowboy/dotfiles)

Mac と Ubuntu 用。ディレクトリ分けがされていて、ROOT には何も置いてない。
bin/dotfiles が bootstrap 用の script そこそこの大きさ。
copy は cp, link は symlink, config は.config 下に symlink, init は setup script を bin/dotfiles からよしなにやっている。
bash 使い。実行順や読み込み順はファイル名`[0-9][0-9]_hogehoge.sh`のように管理されている。

## [officel/dotfiles](https://github.com/officel/dotfiles)

package 管理に Brew, aqua で行っている。
go-task の Taskfile という yaml でタスクを定義している。
XDG_CONFIG_HOME 利用。bash 使い。

## [amacgregor/dot-files](https://github.com/amacgregor/dot-files)

oh-my-zsh, vim, tmux 使い
asdf 利用しているみたいだが、dot-files の中には設定はなし。
bootstrap 用のスクリプトも無いみたい。シンプル。

## [webpro/dotfiles](https://github.com/webpro/dotfiles)

mac がメイン、Ubuntu や Arch でも使えるようにしてしているよう。
タスクランナーに Makefile を使っている。
bash 使い。
bash のテスティングフレームワーク bats を利用したテストが含まれている。
mac では brew, arch に pacman。vscode の extensions もファイル管理されている。

## [theniceboy/.config](https://github.com/theniceboy/.config)

bin/upgrade-all が bootstrap script、python3 で書いてある。
zsh 使い。
メインは Mac っぽいけど、Linux でも Brew を使っていそうな雰囲気。
brew bundle は使わず script 内にパッケージ列挙、mac と linux で分離するのも script 内にしている。

## [alrra/dotfiles](https://github.com/alrra/dotfiles)

bash 使い。
bashrc.local など個人設定でカスタマイズを読み込むような設計になっている。
src/os/setup.sh が bootstrap script。bash 製
home 下に clone じゃなくて~/projects/dotfiles においておくことを想定している。
mac と ubuntu 用。
mac は brew, ubuntu は apt-get
かなり setup 用の script を分割して管理している。

## [skwp/dotfiles](https://github.com/skwp/dotfiles)

install.sh が bootstrap script。対話的にセットアップするのにも対応している。
タスクランナーに rake を使っている。
普段の開発環境に docker や docker-compose を利用しているっぽい。
zsh で prezto 使い。
brew 利用だが、Mac のみで分岐している。おそらく Mac メイン使い。
package は Rakefile の中に直接定義されている。
Ruby/Rails 使いの方。

## [paulirish/dotfiles](https://github.com/paulirish/dotfiles)

Mac 使い、setup のための shellscript がいくつかある。shellcheck のテストもある。symlink をスクリプトで貼っている。
bash メインだが、fish の設定もありたまに使っている様子。
brew と npm でパッケージ管理。

## [momeemt/config](https://github.com/momeemt/config)

https://zenn.dev/momeemt/articles/dotfiles2025

Nix 利用
タスクランナーに casey/just を利用
お試し用の devcontainer も準備されている。
どうでもいいけど、.github/README.md を置いてもメインに表示されるんだ。
初めて Nix が使われているのを見たが、Nix がわからないと、何がなんだかわからない…なんかすごい。
設定がほぼ全て、`.nix`ファイルで定義されている。
中を見るより、記事を見たほうが学びが多かった。

## [serna37/dotfiles](https://github.com/serna37/dotfiles)

https://note.alhinc.jp/n/n60e2178fa73d

Mac 用。zsh 使い。
install.sh に brew のパッケージが書かれていたり、symlink を貼るのが書かれていたり
シンプル
mise が使われている。パッケージマネージャっぽいけどグローバルなタスクランナーみたいな使い方もできるのかな？

## [tadashi-aikawa/owl-playbook](https://github.com/tadashi-aikawa/owl-playbook/tree/master)

https://minerva.mamansoft.net/%F0%9F%93%97Productivity%E3%82%92%E4%B8%8A%E3%81%92%E3%82%8B%E3%81%9F%E3%82%81%E3%81%AB%E5%A4%A7%E5%88%87%E3%81%AA100%E3%81%AE%E3%81%93%E3%81%A8/%F0%9F%93%97dotfiles%E3%82%92%E8%82%B2%E3%81%A6%E3%82%8B

window と Linux で設定が別れている。
bash と zsh の設定があるが、zsh メインっぽそう。
win は scoop/npm/go
linux は apt と mise
どちらもそれぞれ bootstrap のスクリプトでコネコネしている。
タスクランナーに go-task

## [happy663/dotfiles](https://github.com/happy663/dotfiles)

https://techblog.cartaholdings.co.jp/entry/dotfiles-toyama
Mac と Linux
タスクランナーに make
nix 利用
