# GitHub Actions Deployment Setup

## Using Personal Access Token for Private Repository Access

The GitHub Actions workflow needs access to the private corporate repository. We'll use a Personal Access Token (PAT) which is more reliable than SSH deploy keys.

### Step 1: Create a Classic Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click: **Generate new token** → **Generate new token (classic)**
3. Note: `GitHub Actions Corporate Repository Access`
4. Expiration: Choose appropriate duration (recommend 1 year)
5. Select scopes:
   - ✅ **repo** (Full control of private repositories)
6. Click: **Generate token**
7. **Copy the token immediately** (you won't see it again!)

### Step 2: Add Token as Repository Secret

1. Go to the **public repository**: https://github.com/fwornle/agentic-ai-nano
2. Navigate to: Settings → Secrets and variables → Actions
3. Delete old secrets if they exist:
   - `CORPORATE_ACCESS_TOKEN`
   - `CORPORATE_DEPLOY_KEY`
4. Click: **New repository secret**
5. Name: `CORPORATE_PAT`
6. Secret: Paste the Personal Access Token from Step 1
7. Click: **Add secret**

### Step 3: Push Updated Workflow

The workflow uses token authentication. Push the changes:

```bash
git add .github/workflows/deploy-pages.yml DEPLOYMENT_SETUP.md
git commit -m "fix: switch to Personal Access Token for repository access"
git push origin-public main
```

## Alternative: SSH Deploy Key Method (if preferred)

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