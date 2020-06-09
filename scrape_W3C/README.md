# Scraping the W3C Mailing Lists

- mailinglist url: lists.w3.org

- time frame: 1997 - 2020

## Basic Characteristics


- number of mailing lists: 1579

- total number of emails: 1.9 million

- number of emails per mailing list: average: 1008, standard deviation: 2974

- number of conversations per mailing list: average 16.5, standard deviation: 41

- number of emails per conversation: average 3.5, standard deviation: 4.8




## The Corpus

The hierarchical structure of the W3C mailinglist archives is `[mailinglist]/[time period]/[subject string]/[email]`. Rather than collecting all emails into one set, we keep this structure so that we can later readily recover conversations and their organisational and temporal contexts.


### Listings

- [mailinglists.json](LINK HERE): a plain list of the names of the mailinglists listed on https://lists.w3.org

- [periods.json](LINK HERE): a dict which lists the time period names (such as `2002Aug`) per mailinglist

- [subjects](LINK HERE): each file (named by a mailinglist, e.g. `html-tidy.json`) contains a list of lists of subject strings; each of the sublists corresponds (by index) to a period (as listed in `periods.json`); hence, each file is a list of lists (each subject in each sublist is actually a tuple consisting of the subject string itself and a list of the names of the emails in that subject)

- 

### Stats (Theoretical)

The archives hierarchically list mailinglists, time periods, subject and emails; the _theoretical_ numbers are
those obtained from the pages which list these hierarchies (which were in fact also used to enumerate the links to the emails to download). 

- mailinglists: 1597

- time periods: 37681 in total; <br> see `periods.json` for the lists of periods per mailinglist; <br> 406 mailinglists do not have any time periods (partly due to parsing issues)

- subjects: 712782 in total; this is also the number of conversations;<br> see `subjects` for the listings where the numbers of subjects per mailinglist can be obtained; <br> each mailinglist contains an average of 446 subjects (i.e. conversations; std dev 1637)

- emails: 1886020 in total; each mailinglist has an average of 1180 emails (std dev 4905)

Additionally, the pages listing the time periods of each mailinglist indicate the number of emails per time period. These numbers can be used to check the number numbers of obtained download links and emails against, to know how many fall through the cracks due to server or parsing errors. 


### Omitted Data

Email(s) omitted in the case of:

- mailinglist does not have a time period listing in the standard W3C archive format (some older lists and announcement lists)

- subject lists unparseable, either wholly or partly (mainly due to inconsistent character encodings)

- 



