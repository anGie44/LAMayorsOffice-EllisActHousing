## Ben Fisher bensfisher@gmail.com ##
setwd('~/LAMayorsOffice-EllisActHousing/')
library(dplyr)

df = read.csv('~/Downloads/la_housing_dataset_no_geo_property_id_cleanzip2.csv', stringsAsFactors = F)
df$X = NULL # get rid of index column

ellis = df %>% # get ellis act properties
  filter(General.Category=='Ellis Withdrawal') %>%
  select(Property.ID, Status.Date, Address.Full, Zip.Code)

res = df %>% # get rows where there are permits for new apartments or houses
  filter(Permit.Sub.Type=='Apartment' | Permit.Sub.Type=='1 or 2 Family Dwelling')

res_check = merge(ellis, res, by='Property.ID', all.x=T)# merge

res_check = res_check %>% # check which ones are violating the five year window
  filter(Status=='CofO Issued' | Status=='CofO Corrected' | Status=='CofO in Progress'
         | Status=='TCO Issued' | Status=='TCO Renewed' | Status=='Permit Expired' |
           Status=='CofO Superseded' | Status=='Insp Scheduled') %>%
  mutate(ellis_date = as.Date(Status.Date.x, format='%m/%d/%y')) %>%
  mutate(permit_date = as.Date(Status.Date.y, format='%m/%d/%y')) %>%
  mutate(deadline = ellis_date+(5*365.25)) %>%
  mutate(past_deadline = ifelse(deadline<Sys.Date(), 'no', 'yes')) %>%
  mutate(years = (permit_date-ellis_date)/365.25) %>%
  mutate(violation = ifelse((years>-1 & years<5),1,0)) %>% # potential violations id'd by permits filed 1 year before or 5 years after withdrawal
  mutate(prop_dup = duplicated(Property.ID)) %>%
  mutate(date_dup = duplicated(Status.Date.y)) %>%
  filter(prop_dup == FALSE & date_dup==FALSE) 

res_check = res_check %>% # clean up to write to csv
  filter(violation==1) %>% # get violations only
  select(Property.ID, Address.Full.x, Zip.Code.x, ellis_date, permit_date,
         Permit.Type, Permit.Sub.Type, Work.Description, years, deadline, past_deadline)
names(res_check) = c('Property.ID', 'Address.Full', 'Zip.Code', 'ellis_date', 'permit_date',
                 'Permit.Type', 'Permit.Sub.Type', 'Work.Description', 'years', 'deadline', 
                 'past_deadline')

write.csv(res_check, 'potential_violations.csv', row.names=F)
