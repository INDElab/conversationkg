{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Corpus and Parsing\n",
    "\n",
    "W3C mailing list crawled and parsed in 2005: https://tides.umiacs.umd.edu/webtrec/trecent/parsed_w3c_corpus.html <br>\n",
    " - Original dataset has around 170k e-mails\n",
    " - After processing around 140k remain; rest is dropped due to missing/inconsistent information"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Processing Pipeline\n",
    "\n",
    " 1. parse e-mail headers (lines at the top of each e-mail in field=value format) (see `parse_headers.ipynb`):\n",
    "   - extract sender address, receiver, subject, etc\n",
    "   - extract time sent and parse into Python object\n",
    "   - extract e-mail id, a unique identifier -> used to link e-mails by field inreplyto\n",
    "   \n",
    "   \n",
    " 2. parse e-mail bodies, for now (see `parse_bodies.ipynb`):\n",
    "   - convert to UTF-8 encoding (original latin-1) and unescape HTML entities\n",
    "   - identify and remove quoted text (usually starts with > or | and introduced by a line with info about the previous e-mail)\n",
    "   - extract URIs (i.e. HTTP links and e-mail addresses) mentioned in the body\n",
    "   \n",
    "   \n",
    " 3. sort e-mails by time sent and group into conversations according to fields id and inreplyto (see `group_conversations.ipynb`)\n",
    " \n",
    "=> conversations are the central entities in the graph we are building"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Extraction of Entities and Graph Structure\n",
    "\n",
    " - an Email has entities such Persons, Organisations and Links/Addresses and relations such as Sender(Email, Person), BelongsTo(Person, Organisation), Mentions(Email, Link)\n",
    " \n",
    " - a Conversation is simply a list of Email, leading to the relation EvidencedBy(Conversation, [Email_1, ..., EMail_n]), and inherits the relations of the Emails it consists of, that is e.g. Mentions(Conversation, Link)\n",
    "\n",
    "see `extract_everything.ipynb`"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Provenance\n",
    "\n",
    " - to be able to recall where a fact or entity is from, store the id of the e-mail(s) it was extracted from\n",
    " - introduce two relations: EvidencedBy and MentionedBy, e.g. EvidencedBy(Person, Email) or MentionedBy(Org, Email), that are stored in an additinal ledger"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
