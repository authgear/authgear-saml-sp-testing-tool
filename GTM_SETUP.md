# Google Tag Manager Setup

This application supports Google Tag Manager (GTM) for analytics and tracking. The GTM ID is configured via environment variables to avoid committing sensitive information to the repository.

## Setup Instructions

### 1. Get Your GTM Container ID

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Create a new account or select an existing one
3. Create a new container for your website
4. Copy the Container ID (format: `GTM-XXXXXXX`)

### 2. Configure for Local Development

For local development, set the environment variable:

```bash
export GTM_ID="GTM-XXXXXXX"
```

Or add it to your `.env` file (if using one):

```
GTM_ID=GTM-XXXXXXX
```

### 3. Configure for Production Deployment

#### Option A: Using Helm Values (Recommended)

Update your `deploy/helm/values.yaml` file:

```yaml
images:
  app: "quay.io/theauthgear/authgear-saml-sp-testing-tool"

# Google Tag Manager ID
gtmId: "GTM-XXXXXXX"
```

#### Option B: Using Environment Variables in CI/CD

In your GitHub Actions workflow or CI/CD pipeline, set the environment variable:

```yaml
# Example for GitHub Actions
env:
  GTM_ID: ${{ secrets.GTM_ID }}
```

And add `GTM_ID` as a repository secret in GitHub:
1. Go to your repository settings
2. Navigate to Secrets and variables → Actions
3. Add a new repository secret named `GTM_ID`
4. Set the value to your GTM container ID

#### Option C: Using Kubernetes Secrets

Create a Kubernetes secret:

```bash
kubectl create secret generic gtm-secret --from-literal=GTM_ID=GTM-XXXXXXX
```

Then update the Helm deployment to use the secret:

```yaml
# In deploy/helm/templates/app.yaml
env:
  - name: GTM_ID
    valueFrom:
      secretKeyRef:
        name: gtm-secret
        key: GTM_ID
```

### 4. Verify Installation

1. Deploy your application
2. Open the website in your browser
3. Open Developer Tools (F12)
4. Check the Console for any GTM-related errors
5. Verify that the GTM script is loaded in the Network tab
6. Use the Google Tag Manager Preview mode to test your setup

### 5. Security Considerations

- ✅ GTM ID is not committed to the repository
- ✅ Environment variable approach keeps sensitive data out of version control
- ✅ GTM only loads when the ID is provided
- ✅ No tracking occurs when GTM_ID is empty or not set

### 6. Disabling GTM

To disable GTM tracking:

- **Local development**: Don't set the `GTM_ID` environment variable
- **Production**: Set `gtmId: ""` in your Helm values or don't set the environment variable

## Troubleshooting

### GTM Not Loading

1. Check that the `GTM_ID` environment variable is set correctly
2. Verify the container ID format (should be `GTM-XXXXXXX`)
3. Check browser console for JavaScript errors
4. Ensure your GTM container is published

### GTM Loading but No Data

1. Verify your GTM container is properly configured
2. Check that tags are published in GTM
3. Use GTM Preview mode to debug
4. Verify that your domain is allowed in GTM settings

## Additional Resources

- [Google Tag Manager Documentation](https://developers.google.com/tag-manager)
- [GTM Setup Guide](https://support.google.com/tagmanager/answer/6103696)
- [GTM Best Practices](https://support.google.com/tagmanager/answer/6102821) 