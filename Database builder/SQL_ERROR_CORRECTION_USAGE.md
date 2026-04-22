# SQL Error Correction Feature - User Guide

## Quick Start

### When Deployment Fails

1. **View Execution Logs** (Step 7)
   - After clicking "Deploy Schema", scroll to "SQL Execution Logs" section
   - See a table showing each SQL statement and its status
   - Failed statements are highlighted in red with error messages

2. **Copy Error Information**
   - Find the failed statement in the logs
   - Copy the error message shown in the "Message" column

3. **Fix the SQL** (Step 8)
   - Scroll to "SQL Error Correction" section
   - Paste the error message in "Paste Error Message" field
   - Paste the failed SQL in "Failed SQL Statement" field
   - Click "Get Corrected SQL"

4. **Review Corrected SQL**
   - The LLM will analyze the error and provide a corrected version
   - Review the corrected SQL to ensure it looks right

5. **Redeploy**
   - Click "Redeploy with Corrected SQL"
   - The corrected statement will be executed
   - New execution logs will show the result

## Understanding Execution Logs

### Log Table Columns

| Column | Description |
|--------|-------------|
| Statement # | Which SQL statement this is (1, 2, 3, etc.) |
| Status | ✓ success, ✗ failed, ⏳ pending |
| SQL | First 100 characters of the SQL statement |
| Message | Error message if failed, or empty if successful |

### Status Colors

- **Green (✓ success)** - Statement executed successfully
- **Red (✗ failed)** - Statement failed with an error
- **Yellow (⏳ pending)** - Statement is waiting to execute

## Error Correction Workflow

### Example: Snowflake Schema Error

**Scenario:** You're deploying to Snowflake and get an error about table name format.

**Steps:**

1. **See the error in logs:**
   ```
   Statement 1: ✗ failed
   Error: "Identifier must be quoted"
   ```

2. **Copy error and SQL:**
   - Error: `Identifier must be quoted`
   - SQL: `CREATE TABLE student (id INT PRIMARY KEY)`

3. **Paste into correction dialog:**
   - Error Message: `Identifier must be quoted`
   - Failed SQL: `CREATE TABLE student (id INT PRIMARY KEY)`

4. **Get corrected SQL:**
   - LLM returns: `CREATE TABLE "STUDENT" (ID INT PRIMARY KEY)`

5. **Redeploy:**
   - Click "Redeploy with Corrected SQL"
   - Statement executes successfully

## Common Errors and Fixes

### Error: "Table already exists"
- **Cause:** Table was partially created in previous attempt
- **Fix:** Drop the table manually or use a different schema name

### Error: "Column type not recognized"
- **Cause:** Database doesn't support the data type
- **Fix:** LLM will suggest compatible data type (e.g., VARCHAR instead of TEXT)

### Error: "Invalid schema name"
- **Cause:** Schema doesn't exist or user lacks permissions
- **Fix:** Verify schema name in credentials and user permissions

### Error: "Syntax error"
- **Cause:** SQL syntax is invalid for the target database
- **Fix:** LLM will correct syntax for the specific database

## Tips for Success

1. **Check Credentials First**
   - Ensure database credentials are correct before deploying
   - Verify user has CREATE TABLE permissions

2. **Review Schema Design**
   - Check the generated schema in Step 5 before deploying
   - Verify table names and column types look correct

3. **Use Meaningful Error Messages**
   - Copy the complete error message from logs
   - Include any error codes or line numbers

4. **Test with Small Files First**
   - Start with a small CSV to test the workflow
   - Once working, use larger files

5. **Keep Error Messages**
   - Don't modify error messages when pasting
   - Include full error text for better LLM analysis

## Troubleshooting

### Corrected SQL Still Fails
- The error might be more complex than the LLM can fix
- Try manually editing the SQL based on the error message
- Check database documentation for the specific error code

### Correction Takes Too Long
- The LLM might be processing a complex error
- Wait for the response (usually 5-30 seconds)
- If it times out, try again with a simpler error message

### Can't See Execution Logs
- Make sure deployment completed (check status message)
- Scroll down to Step 7 section
- Try refreshing the page if logs don't appear

### Error Correction Dialog Not Showing
- Only appears if deployment has failed statements
- Check if all statements succeeded (no red X marks)
- Try deploying again to trigger the dialog

## Advanced Usage

### Batch Corrections
- Currently corrects one statement at a time
- For multiple failures, correct and redeploy each one
- Future versions may support batch correction

### Custom SQL Fixes
- You can manually edit the corrected SQL before redeploying
- Click in the corrected SQL box to edit
- Make sure syntax is valid for your database

### Saving Corrections
- Corrected SQL is not automatically saved
- Copy corrected SQL to a text file if you want to keep it
- Future versions may add save/history feature

## Database-Specific Notes

### Snowflake
- Table names are uppercase by default
- Schema name is required (usually PUBLIC)
- Warehouse must be running for deployment

### PostgreSQL
- Table names are lowercase by default
- Schema name is optional (defaults to public)
- User must have CREATE privilege

### MySQL
- Table names are case-sensitive on Linux, not on Windows
- No schema concept (use database instead)
- InnoDB is recommended for transactions

### SQL Server
- Table names can be quoted with brackets [table_name]
- Schema name is required (usually dbo)
- User must have CREATE TABLE permission

### Athena
- Tables are created in S3 location
- Schema name is the database name
- Requires S3 output location for queries

## Getting Help

If you encounter issues:

1. **Check the error message** - It usually tells you what's wrong
2. **Review the SQL** - Look for obvious syntax errors
3. **Check database permissions** - Ensure user can create tables
4. **Try a simpler schema** - Start with fewer tables/columns
5. **Check database documentation** - For database-specific syntax

## Next Steps

After successful deployment:

1. Verify tables were created in your database
2. Check table structure matches your expectations
3. Load sample data to test
4. Set up indexes and constraints as needed
5. Configure backups and maintenance

---

**Need more help?** Check the main README.md or IMPLEMENTATION_NOTES.md for additional information.
