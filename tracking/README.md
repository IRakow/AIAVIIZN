# 📋 HOW TO CONTINUE IN NEW CHATS

## TO START A NEW SESSION:

Just say one of these:
- "Continue page processing"
- "Process next page"
- "Continue where we left off"

## CLAUDE WILL:
1. Read the state from /tracking/state.json
2. See what's next to process
3. Process that page completely
4. Update all tracking files
5. Tell you what's next

## CURRENT STATUS:
- **Next Page:** https://celticprop.appfolio.com/reports
- **Processed:** 0 pages
- **In Queue:** 15 pages

## ONE PAGE PER CHAT:
Each chat session processes ONE complete page:
- Captures with Playwright
- Extracts formulas
- Creates template
- Stores in Supabase
- Updates tracking

## IF CHAT GETS LONG:
Just start a new chat and say "Continue page processing"

## FILES THAT PERSIST:
- `/tracking/state.json` - Current progress
- `/tracking/processed.json` - Completed pages
- `/tracking/queue.json` - Pages to do
- `/tracking/formulas.json` - All calculations found
- `/tracking/data_mappings.json` - Database references

## EXAMPLES:

**Chat 1:**
You: "Process the reports page"
Claude: [Processes reports, saves everything]
Result: ✅ Reports done

**Chat 2 (new chat):**
You: "Continue processing"
Claude: [Reads state, processes rent_roll]
Result: ✅ Rent roll done

**Chat 3 (new chat):**
You: "What's next?"
Claude: [Checks state, shows income_statement is next]

## READY TO START:
Say "Process the reports page" to begin!