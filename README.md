# Setting Up pgvector for PostgreSQL

This repository uses `pgvector`, a PostgreSQL extension for vector similarity search. Below are the steps to manually install and configure `pgvector` on your system.

---

## Installation Procedure

Follow these steps to set up `pgvector`:

### 1. Install Prerequisites
Ensure you have the necessary tools to build and install PostgreSQL extensions:

```bash
sudo apt update
sudo apt install git make gcc postgresql-server-dev-14
