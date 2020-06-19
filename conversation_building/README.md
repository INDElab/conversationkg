# Building Conversation Objects and Graphs from the Scraped W3C Emails


## Moving Parts

### 1. Extracting Quoted Text:
   - Emails are already sorted into conversations, so quoted text in a reply can be identify via per-line string distance from previous emails
   - use a library: [email-reply-parser](https://github.com/zapier/email-reply-parser)
