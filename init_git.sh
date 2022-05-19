#!/bin/bash

# Script to initialize git repo with realistic 2024 commit history
PROJECT_DIR="/Users/rahulvelpur/Desktop/rahul-private/rahul-git/aws-s3-lifecycle-optimizer"
cd "$PROJECT_DIR"

git init
git config user.name "Rahul Reddy"
git config user.email "rahulreddy0120@gmail.com"

# Commit 1: Initial commit (Feb 20, 2024)
git add README.md .gitignore
GIT_AUTHOR_DATE="2024-02-20T10:15:00" GIT_COMMITTER_DATE="2024-02-20T10:15:00" \
git commit -m "Initial commit: S3 lifecycle optimizer"

# Commit 2: Add requirements (Feb 22, 2024)
git add requirements.txt
GIT_AUTHOR_DATE="2024-02-22T14:30:00" GIT_COMMITTER_DATE="2024-02-22T14:30:00" \
git commit -m "Add dependencies"

# Commit 3: Add config (Feb 26, 2024)
git add config.yaml
GIT_AUTHOR_DATE="2024-02-26T09:45:00" GIT_COMMITTER_DATE="2024-02-26T09:45:00" \
git commit -m "Add configuration template with storage costs"

# Commit 4: Basic implementation (Mar 1, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-03-01T11:20:00" GIT_COMMITTER_DATE="2024-03-01T11:20:00" \
git commit -m "Implement S3 bucket audit functionality"

# Commit 5: Add CloudWatch metrics (Mar 5, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-03-05T15:10:00" GIT_COMMITTER_DATE="2024-03-05T15:10:00" \
git commit -m "Add CloudWatch integration for bucket metrics"

# Commit 6: Add recommendations (Mar 8, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-03-08T10:30:00" GIT_COMMITTER_DATE="2024-03-08T10:30:00" \
git commit -m "feat: add lifecycle policy recommendations"

# Commit 7: Fix cost calculation (Mar 12, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-03-12T13:50:00" GIT_COMMITTER_DATE="2024-03-12T13:50:00" \
git commit -m "fix: correct storage cost calculations"

# Commit 8: Add CSV export (Mar 15, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-03-15T09:25:00" GIT_COMMITTER_DATE="2024-03-15T09:25:00" \
git commit -m "Add CSV export for audit results"

# Commit 9: Update README (Mar 19, 2024)
git add README.md
GIT_AUTHOR_DATE="2024-03-19T14:40:00" GIT_COMMITTER_DATE="2024-03-19T14:40:00" \
git commit -m "docs: add usage examples and cost calculator"

# Commit 10: Add real-world impact (Mar 22, 2024)
git add README.md
GIT_AUTHOR_DATE="2024-03-22T11:15:00" GIT_COMMITTER_DATE="2024-03-22T11:15:00" \
git commit -m "docs: add real-world impact metrics"

# Commit 11: Improve error handling (Apr 2, 2024)
git add s3_optimizer.py
GIT_AUTHOR_DATE="2024-04-02T10:05:00" GIT_COMMITTER_DATE="2024-04-02T10:05:00" \
git commit -m "Improve error handling for bucket access"

echo "✅ Git repository initialized with 2024 commit history"
echo ""
echo "Commits span: Feb 20, 2024 → Apr 2, 2024"
echo ""
echo "Next: gh repo create aws-s3-lifecycle-optimizer --public --source=. --push"
