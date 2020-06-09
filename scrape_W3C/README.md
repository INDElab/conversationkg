# Scraping the W3C Mailing Lists


The World Wide Web Consortium (W3C) is a core standardising body of the internet, developing and deciding standards such as HTML and providing support. In their mailing lists, members of the W3C as well as other organisations, private persons and automated mail agents interact, inquire and announce around concepts, standards and events pertaining to the internet. These mailinglists exist since 1997 and are publicly available on the W3C's mailinglist archives, at https://lists.w3.org/Public/Archives. We have scraped and processed these archives and publish them as a corpus of email conversations.


## The Corpus

The hierarchical structure of the W3C mailinglist archives is `[mailinglist]/[time period]/[subject string]/[email]`. Rather than collecting all emails into one set, we keep this structure so that we can later readily recover conversations and their organisational and temporal contexts.

### Listings

- [mailinglists.json](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C/collected_listings/mailinglists.json): a plain list of the names of the mailinglists listed on https://lists.w3.org

- [periods.json](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C/collected_listings/periods.json): a dict which lists the time period names (such as `2002Aug`) per mailinglist

- [subjects](https://github.com/pgroth/conversationkg/blob/master/scrape_W3C/collected_listings/subjects/): each file (named by a mailinglist, e.g. `html-tidy.json`) contains a list of lists of subject strings; each of the sublists corresponds (by index) to a period (as listed in `periods.json`); hence, each file is a list of lists (each subject in each sublist is actually a tuple consisting of the subject string itself and a list of the names of the emails in that subject)

### Stats (Theoretical)

The archives hierarchically list mailinglists, time periods, subject and emails; the _theoretical_ numbers are
those obtained from the pages which list these hierarchies (which were in fact also used to enumerate the links to the emails to download). 

- mailinglists: 1597

- time periods: 37681 in total; <br> see `periods.json` for the lists of periods per mailinglist; <br> 406 mailinglists do not have any time periods (partly due to parsing issues)

- subjects: 712782 in total; this is also the number of conversations;<br> see `subjects` for the listings where the numbers of subjects per mailinglist can be obtained; <br> each mailinglist contains an average of 446 subjects (i.e. conversations; std. dev. 1637)

- emails: 1886020 in total; each mailinglist has an average of 1180 emails (std dev 4905)

Additionally, the pages listing the time periods of each mailinglist indicate the number of emails per time period. These numbers can be used to check the number numbers of obtained download links and emails against, to know how many fall through the cracks due to server or parsing errors. These numbers suggest that there should be a total of 1975451 emails. 
NB: upon manual inspections, these numbers are not always accurate but still useful as rough indication.
Can be found in `numbers.json`, a dict of lists, listing the numbers of emails per time period and mailinglist.


### Stats (Real)

These refer to the actual stats of the published corpus.

- mailinglists: 1192

- time periods: 37526

- subjects: 705201

- emails: 1876156 in total; on average 6 per subject (std. dev. 11)


### Omitted Data

Email(s) omitted in the case of:

- mailinglist does not have a time period listing in the standard W3C archive format (some older lists and announcement lists)

- subject lists unparseable, either wholly or partly (mainly due to inconsistent character encodings)

- pages containing the email cannot be parsed (e.g. some pages announce false character encodings, some contain unfixable HTML)

=> altogether, we loose about 10,000 emails which is however less than 1%

