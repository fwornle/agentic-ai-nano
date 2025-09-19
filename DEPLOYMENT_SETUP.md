# GitHub Actions Deployment Setup

## Setting up SSH Deploy Key for Private Submodule

The GitHub Actions workflow needs access to the private corporate repository. Follow these steps:

### Step 1: Generate SSH Key Pair

Run this command locally (no passphrase):

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github-deploy-key -N ""
```

This creates two files:
- `~/.ssh/github-deploy-key` (private key)
- `~/.ssh/github-deploy-key.pub` (public key)

### Step 2: Add Deploy Key to Corporate Repository

1. Go to the **corporate repository**: https://github.com/fwornle/agentic-ai-nano-corporate
2. Navigate to: Settings → Deploy keys → Add deploy key
3. Title: `GitHub Actions Deployment`
4. Key: Paste contents of `~/.ssh/github-deploy-key.pub`
5. Check: ✅ **Allow write access** (important!)
6. Click: Add key

### Step 3: Add Private Key to Public Repository Secrets

1. Go to the **public repository**: https://github.com/fwornle/agentic-ai-nano
2. Navigate to: Settings → Secrets and variables → Actions
3. Delete old secret: `CORPORATE_ACCESS_TOKEN` (if exists)
4. Click: New repository secret
5. Name: `CORPORATE_DEPLOY_KEY`
6. Secret: Paste contents of `~/.ssh/github-deploy-key` (the private key)
7. Click: Add secret

### Step 4: Push Updated Workflow

The workflow has been updated to use SSH authentication. Push the changes:

```bash
git add .github/workflows/deploy-pages.yml
git commit -m "fix: use SSH deploy key for private repository access"
git push origin-public main
```

## Alternative: Using Personal Access Token (if SSH doesn't work)

If you prefer to use a Personal Access Token instead:

### Creating a Classic PAT

1. Go to: https://github.com/settings/tokens
2. Click: Generate new token → Generate new token (classic)
3. Note: `GitHub Actions Corporate Access`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click: Generate token
6. Copy the token immediately

### Update Workflow for PAT

If using PAT, revert the workflow changes:

```yaml
- name: Checkout corporate submodule
  uses: actions/checkout@v4
  with:
    repository: fwornle/agentic-ai-nano-corporate
    token: ${{ secrets.CORPORATE_ACCESS_TOKEN }}
    path: docs-content/corporate-only
```

And add the token as `CORPORATE_ACCESS_TOKEN` secret instead.

## Troubleshooting

### 403 Error
- Ensure the deploy key has **write access** enabled
- For PAT: Ensure it's a **classic** token with `repo` scope
- Verify the repository name is correct

### 404 Error
- Check if the user has access to the private repository
- Verify the repository URL is correct

### SSH Key Issues
- Ensure no passphrase was set on the SSH key
- Copy the entire key including `-----BEGIN` and `-----END` lines
- No extra whitespace or newlines