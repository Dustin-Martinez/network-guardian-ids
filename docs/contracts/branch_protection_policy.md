# Repository Branch Protection & Governance Policy

This document outlines the version control policies and security rulesets enforced across the entire **Network Guardian IDS** repository.

---

## 1. Protection Scope

Branch protection rules are applied to the `main` branch only. Feature
branches accept direct pushes from their owners.

* **Effect on Team Members:** Direct pushes to `main` are blocked. All
  merges into `main` must go through a Pull Request. Direct pushes to
  your own feature branch are allowed and expected.
* **Effect on Project Manager (Kit Dustin):** Added to the bypass list
  as Repository Administrator with `Always` permissions, allowing
  hotfixes and rapid integration on `main` without waiting for review
  locks.
---

## 🛠️ 2. Rule Configuration Matrix

The following parameters are actively enforced under GitHub Repository Rulesets:

| Configuration Setting | Enforced State | Operational Effect |
| :--- | :--- | :--- |
| Rule Target | `main` only | Rules apply only to the `main` branch. Feature branches are unrestricted. |
| **Bypass List** | `Repository Admin` (`Always`) | Project Manager retains unrestricted direct push and single-actor merge authority. |
| **Require a pull request before merging** | `ENABLED` | Code must be reviewed via PR before being integrated. |
| **Required Approvals** | `1 Approval` | At least one teammate must review and approve code contributions. |
| **Dismiss stale approvals on new commits** | `ENABLED` | If new commits are pushed to an open PR, prior approvals are invalidated to ensure safety. |
| **Require approval of most recent push** | `DISABLED` | Prevents self-merge blockages for administrative commits. |
| **Block force pushes** | `ENABLED` | Prevents `git push --force` commands from wiping out commit history. |
| **Restrict updates** | `DISABLED` | Allows team members to push update commits to their feature branches freely. |

---

## 🚀 3. Team Pull Request Workflow

Every team member (**Markie, Amber, Kenneth**) must adhere to the following branch workflow:

### Step 1: Create a Feature Branch
Do not work directly on shared code. Create a dedicated feature branch for your role:
```powershell
git checkout -b feature/role-2-backend-bridge
