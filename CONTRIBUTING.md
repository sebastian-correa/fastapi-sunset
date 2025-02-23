<!-- Inspired by https://github.com/markdownlint/markdownlint/blob/main/CONTRIBUTING.md -->
# Contributing to fastpi_sunset   <!-- omit from toc -->

Hey! Thanks for your intent to contribute to the package! This document will help answer common
questions you may have during your first contribution. Please, try to follow these guidelines when
you do so.

## Table of contents  <!-- omit from toc -->
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Code Contribution workflow](#code-contribution-workflow)
- [Issue Reporting](#issue-reporting)
  - [Submitting An Issue](#submitting-an-issue)
- [Code style guide](#code-style-guide)
- [Commit style guide](#commit-style-guide)
- [Pull Request Requirements](#pull-request-requirements)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Code Contribution workflow

Here's the contributing workflow:

1. [Open an issue](#issue-reporting).
1. If it is decided that the issue needs to be worked on, then:
   1. [Fork the project](https://github.com/sebastian-correa/fastapi-sunset/fork).
   2. Create your feature branch (`git switch -c my-new-feature`).
   3. Set up your local environment by running:
      1. `uv sync` to install dependencies.
      2. `uv run pre-commit install --install-dependencies` to install pre-commit hooks.
   4. Make and commit your changes (`git commit -m 'Add some feature'`).
      1. Please follow the [code](#code-style-guide) and [commit](#commit-style-guide) style guides.
   5. Push to the branch (`git push origin my-new-feature`).
1. [Create a Pull Request](https://github.com/sebastian-correa/fastapi-sunset/compare) for your
   change, following all [pull request requirements](#pull-request-requirements). You should
   probably point your changes to `main`.
1. Participate in the code review process with the project maintainers until they merge the code
   into `main`.

> [!NOTE]
> While we encourage you to follow the guide as closely as possible, we still prefer you submit your
> contribution even if imperfect than you not contributing due to too many requirements.

## Issue Reporting

Not every contribution comes in the form of code. Submitting, confirming, and triaging issues is an
important task for any project. We use GitHub to track all project issues.

If you discover bugs, have ideas for improvements or new features, please start by [opening an issue](https://github.com/sebastian-correa/fastapi-sunset/issues/new).
Ideally, that issue should be used to discuss the situation and agree on a plan of action before
writing code or submitting a pull request.

If you want to ask a how-to question or similar, it's probably better to [start a discussion](https://github.com/sebastian-correa/fastapi-sunset/discussions/new/choose).

### Submitting An Issue

- Check that the issue has not already been reported.
- Check that the issue has not already been fixed in `main`.
- Open an issue with a descriptive title and description.
- It's always best to include the output of `python --VV`, the version of the package and your OS
   details.
- Include any relevant code in the issue. If possible, submit a [Minimal Reproducible Example](https://stackoverflow.com/help/minimal-reproducible-example).

## Code style guide

Our Python code and documentation should the [Google Style guide](https://google.github.io/styleguide/pyguide.html).
Don't worry, most of the style guide will be auto enforced by `ruff` (our linter and formatter).

In general, match the coding style of the files you edit. Although everyone has their own
preferences and opinions, which we encourage you to discuss via a [discussion](https://github.com/sebastian-correa/fastapi-sunset/discussions/new/choose),
code contributions are not the right place to debate them.

When type-hinting (mandatory), be sure to be as generic as possible for function arguments (i.e.,
prefer `Iterable[int]` over `list[int]` where possible) and as specific as possible for return types
(most often, you know exactly what you're returning).

## Commit style guide

Our commit style guide is partially enforced by a pre-commit hook. Be sure to:

- Write in the imperative mood. For instance, write `Add X`, `Implement Y`, `Fix Z`. You commit
   message should correctly complete this sentence: *If applied, this commit will...*
- Write a summary line no longer than 72 characters.
- If writing more (encouraged), leave a blank line after the summary line and write the rest below,
   wraped to 72 characters (unless you include URLs).
- Ensure you have atomic commits. Don't use commits as a save button (i.e., don't add commits for
   superfluos things like WIPs, format changes of your own code and such), but don't implement big
   changes in single commits either.

> ![TIP]
> Where possible, we encourage you to sign off (and sign) commits by passing the `-sS` flag.

## Pull Request Requirements

All pull requests must meet these specifications:

- **Title:** The title must start with a capital and not end with any punctuation mark. It should
   also be written in the impartive mood (see [commit style guide](#commit-style-guide)).
- **Tests:** To ensure high quality code and protect against future regressions, we require tests
  for all new/changed functionality. Test positive and negative scenarios.
- **Passed GitHub Actions:** Certain style and code checks will be performed when you submit a PR.
   These must all pass before your PR is merged.
