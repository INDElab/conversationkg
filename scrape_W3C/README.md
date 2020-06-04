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


### Data Structure

- mailinglists.json: a plain list of the names of the mailinglists listed on [lists.w3.org](https://lists.w3.org)


### Stats (Theoretical)

The archives hierarchically list mailinglists, time periods, subject and emails; the _theoretical_ numbers are
those obtained from the pages which list these hierarchies (which were in fact also used to enumerate the emails to download). In addition, the page listing the time periods of each mailinglist indicates the number

- mailinglists: 1597

- time periods: 37681 in total;<br> see `periods.json` for the lists of periods per mailinglist;<br> 406 mailinglists do not have a single period (partly due to parsing issues)

- subjects: 


