# Portfolio Deployment Guide for Render

## Overview

This guide explains how to deploy your Portfolio application to Render, ensuring that all features work correctly, including:

1. The custom admin interface integrated into the site UI
2. Bento grid UI showcase for project detail pages
3. Real-time analytics dashboard with WebSockets
4. Backup and restore system with real-time updates

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Git repository with your portfolio code

## Deployment Steps

### 1. Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Connect your Git repository
4. Use the following settings:
   - **Name**: Your portfolio name (e.g., `my-portfolio`)
   - **Runtime**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `daphne PortfolioProject.asgi:application --port $PORT --bind 0.0.0.0`

### 2. Configure Environment Variables

Add the following environment variables in the Render dashboard:

- `SECRET_KEY`: Set a secure random string (or use Render's auto-generated value)
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: This will be automatically set if you use Render's PostgreSQL

### 3. Database Setup (SQLite)

Since you're using SQLite as your database:

1. Create a persistent disk on Render to store your SQLite database
   - In the Render dashboard, under your web service, go to "Disks"
   - Create a new disk with at least 1GB of space
   - Mount it at `/opt/render/project/src/db`

2. Add an environment variable to update your database path:
   - Add `SQLITE_PATH=/opt/render/project/src/db/db.sqlite3`

3. Before the first deployment, you'll need to copy your existing SQLite database to the persistent disk
   - You can use SFTP or Render's shell to upload your db.sqlite3 file

### 4. WebSockets Configuration

Your WebSocket configuration is already set up with Daphne and channels. No additional configuration is needed as Render supports WebSockets out of the box with Daphne.

### 5. Static and Media Files

1. Static files are handled by WhiteNoise (already configured)
2. For media files, configure render.yaml to use a persistent disk or consider using cloud storage like AWS S3

## Important Notes

### For the Custom Admin Interface
No special configuration is needed as this uses Django views and templates.

### For the Bento Grid UI
Ensure your screenshot uploads work by verifying the media storage settings.

### For the Real-time Analytics Dashboard
Ensure your WebSocket connections are working by testing the dashboard after deployment.

### For the Backup System
Make sure your backups directory has write permissions on Render, or configure to use cloud storage.

## Verify Deployment

After deployment, visit your site and verify:

1. The main site loads correctly
2. You can log in to the admin panel
3. The projects display correctly with the bento grid layout
4. Real-time features work (analytics dashboard updates live)
5. Backup and restore functionality works properly

## Troubleshooting

- Check Render logs for any errors
- Verify all environment variables are set correctly
- Ensure database migrations have been applied properly
- For WebSocket issues, check the Daphne logs specifically
