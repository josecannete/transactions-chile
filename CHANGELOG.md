# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.4.0

### Added
- Added support for new credit card transactions: billed and unbilled for Itaú and Banco de Chile.
- Added a BankTransactionsFactory class to handle the creation of transaction classes based on the bank type.
- Added tests for the new transaction classes and the factory class.

### Changed
- Refactored code by improving the inheritance structure of the transaction classes.
-  The new structure uses enums for banks and account types, and mixins for common functionality.
- Updated the CLI to use the new BankTransactionsFactory for creating transaction classes.

## 0.3.2

### Changed
- Version bump for maintenance release
- Minor improvements and documentation updates

## 0.3.1

### Changed
- Version bump for minor improvements
- Updated documentation and CI configuration

## 0.3.0

### Added
- Comprehensive test suite for bank transaction classes
- CI/CD pipeline with GitHub Actions
- Pre-commit configuration for code quality checks

### Changed
- Refactored test suite to reduce code duplication
- Updated dependencies to latest versions

### Fixed
- Fixed test_validate_and_save_failure to properly handle validation errors