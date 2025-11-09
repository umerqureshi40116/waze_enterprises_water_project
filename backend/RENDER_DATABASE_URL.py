"""Generate the exact DATABASE_URL for Render - copy this EXACTLY"""

DATABASE_URL = "postgresql://neondb_owner:npg_IYnkVx8vrdy3@ep-old-grass-ahuzyjob-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("=" * 80)
print("COPY THIS ENTIRE STRING EXACTLY (ONE LINE, NO BREAKS):")
print("=" * 80)
print(DATABASE_URL)
print("=" * 80)
print(f"\nTotal length: {len(DATABASE_URL)} characters")
print("\nPaste this in Render Dashboard:")
print("  1. Go to https://dashboard.render.com")
print("  2. Click waze-enterprises-water-project-backend")
print("  3. Go to Environment")
print("  4. Key: DATABASE_URL")
print("  5. Value: [paste the URL above as ONE LINE]")
print("  6. Click Save")
