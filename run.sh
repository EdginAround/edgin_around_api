#!/bin/sh

function usage() {
    echo 'Commands:'
    echo ' - mypy - runs `mypy` checker in the main app'
    echo ' - black - runs `black` code formatter'
    echo ' - tests - runs unit tests'
}

function run_mypy() {
    cd python
    python -m mypy edgin_around_api/*.py --show-error-codes $@
    cd ..
}

function run_mypy_tests() {
    cd python
    python -m mypy test/test_*.py --show-error-codes $@
    cd ..
}

function run_black() {
    python -m black ./python --config python/black.toml
}

function run_tests() {
    cd python
    python -m unittest $@
    cd ..
}

function run_package() {
    cd python
    python setup.py sdist
    cd ..
}

if (( $# > 0 )); then
    command=$1
    shift

    case $command in
        'mypy')
            run_mypy $@
            ;;
        'black')
            run_black $@
            ;;
        'tests')
            run_mypy && run_mypy_tests && run_tests $@
            ;;
        'package')
            run_package
            ;;
        *)
            echo "Command \"$command\" unknown."
            echo
            usage
            ;;
    esac
else
    echo 'Please give a command.'
    echo
    usage
fi

