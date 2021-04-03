#!/bin/sh

function usage() {
    echo 'Commands:'
    echo ' - mypy - runs mypy checker in the main app'
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

function run_tests() {
    cd python
    python -m unittest $@
    cd ..
}

if (( $# > 0 )); then
    command=$1
    shift

    case $command in
        'mypy')
            run_mypy $@
            ;;
        'tests')
            run_mypy && run_mypy_tests && run_tests $@
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

