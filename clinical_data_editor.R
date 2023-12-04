source('~/GitHub/danbio.data.extraction.imaging/Denmark/functions/functions_old.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_basdai.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_basfi.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_MASES_score.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_asdas.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_criteria.R')
library(writexl)
library(stringr)
library(readxl)


calc_bio_drug_series_number = function(d_wide){
  
  # Make sure drug list only has bio drugs
  #drug_list = c(bio_drug1,bio_drug2...)
  
  # sort d according to patiet ID, bio drug start date and visit date
  d = d_wide[order(d_wide$patient_id,d_wide$drug_start_date,d_wide$drug_name),]
  
  drug_list = c("abatacept","adalimumab","amgevita",
                "anakinra","baricitinib","belimumab",
                "benepali","certolizumab","erelzi",
                "etanercept","flixabi","golimumab",
                "guselkumab","hyrimoz","imraldi",
                "inflectra","infliximab","ixekizumab",
                "mycophenolat","otezla","biologic_other",
                "project_medicine","remsima","rituximab",
                "rixathon","ruxience","sarilumab",
                "secukinumab","tocilizumab",
                "tofacitinib","upadacitinib","ustekinumab","zessly")
  
  d$bio_drug_series_number = NA
  pid = NA
  old_pid = NA
  num = 1
  for(i in 1:nrow(d)){
    pid = d[i,]$patient_id
    if(!is.na(pid) & !is.na(old_pid) & pid != old_pid){
      num = 1
    }
    old_pid = pid
    
    if(d[i,]$drug_name %in% drug_list){
      d[i,]$bio_drug_series_number = num
      num = num + 1
    }
  }
  return(d)
}

asas_calculator = function(d){
  asas_criteria_1_back_pain=d$asas_criteria_1_back_pain
  asas_criteria_2_arthritis=d$asas_criteria_2_arthritis
  asas_criteria_3_enthesitis=d$asas_criteria_3_enthesitis
  asas_criteria_4_uveitis=d$asas_criteria_4_uveitis
  asas_criteria_5_dactylitis=d$asas_criteria_5_dactylitis
  asas_criteria_6_psoriasis=d$asas_criteria_6_psoriasis
  asas_criteria_7_ibd=d$asas_criteria_7_ibd
  asas_criteria_8_response_to_nsaids=d$asas_criteria_8_response_to_nsaids
  asas_criteria_9_family_history=d$asas_criteria_9_family_history
  asas_criteria_10_hla_b27=d$asas_criteria_10_hla_b27
  asas_criteria_11_elevated_crp=d$asas_criteria_11_elevated_crp
  asas_criteria_12_mri_sacroiliitis=d$asas_criteria_12_mri_sacroiliitis
  asas_criteria_13_xray_sacroiliitis=d$asas_criteria_13_xray_sacroiliitis
  
  # Calculates asas criteria output
  newd = c()
  for (i in 1:length(d$patient_id)){
    asas1 = asas_criteria_1_back_pain[i]
    asas2 = asas_criteria_2_arthritis[i]
    asas3 = asas_criteria_3_enthesitis[i]
    asas4 = asas_criteria_4_uveitis[i]
    asas5 = asas_criteria_5_dactylitis[i]
    asas6 = asas_criteria_6_psoriasis[i]
    asas7 = asas_criteria_7_ibd[i]
    asas8 = asas_criteria_8_response_to_nsaids[i]
    asas9 = asas_criteria_9_family_history[i]
    asas10 = asas_criteria_10_hla_b27[i]
    asas11 = asas_criteria_11_elevated_crp[i]
    asas12 = asas_criteria_12_mri_sacroiliitis[i]
    asas13 = asas_criteria_13_xray_sacroiliitis[i]
    
    asas_list = c(asas1,asas2,asas3,asas4,asas5,asas6,asas7,asas8,asas9,asas10,asas11,asas12,asas13)
    # asas12 == 1 and one SpA feature or asas10 and two SpA features
    asas_sum = 0
    asas_NA = 0
    for (asas in asas_list[1:11]){
      if(!is.na(asas)){
        asas_sum = asas_sum + asas
      }else{
        asas_NA = asas_NA + 1
      }
    }
    if ((((!is.na(asas12) & asas12 == 1 ) | (!is.na(asas13) & asas13 == 1)) & asas_sum > 0) | (!is.na(asas10) & asas10 == 1 & asas_sum > 2)){
      newd = c(newd,1)
    }else{
      if ((!is.na(asas10) & !is.na(asas13) & !is.na(asas12) & asas12 == 0 & asas13 == 0 & asas10 == 0)){
        newd = c(newd,0)
      }else{
        if ((((!is.na(asas12) & asas12 == 1 ) 
              | (!is.na(asas13) & asas13 == 1))
             & asas_sum < 1 & asas_NA < 1)
            | (!is.na(asas12) & !is.na(asas13) & !is.na(asas10) & asas10 == 1 & asas_sum == 1 & asas_NA <= 1)
            | (!is.na(asas12) & !is.na(asas13) & !is.na(asas10) & asas10 == 1 & asas_sum == 2 & asas_NA < 1)){
          newd = c(newd,0)
        }else{
          newd = c(newd,NA)
        }
      }
    }
  }
  d$asas_criteria = newd
  return(d)
}

new_york_calculator = function(d){
  new_york_criteria_1_low_back_pain=d$new_york_criteria_1_low_back_pain
  new_york_criteria_2_lumbar_spine_motion=d$new_york_criteria_2_lumbar_spine_motion
  new_york_criteria_3_chest_expansion=d$new_york_criteria_3_chest_expansion
  if("new_york_criteria_4a_xray_sacroiliitis_bilat" %in% colnames(d) & "new_york_criteria_4b_xray_sacroiliitis_unilat" %in% colnames(d)){
    new_york_criteria_4a_xray_sacroiliitis_bilat=d$new_york_criteria_4a_xray_sacroiliitis_bilat
    new_york_criteria_4b_xray_sacroiliitis_unilat=d$new_york_criteria_4b_xray_sacroiliitis_unilat
  }else if("new_york_criteria_4_sacroiilitis" %in% colnames(d)){
    new_york_criteria_4_sacroiilitis=d$new_york_criteria_4_sacroiilitis
  }
  
  
  
  newd = c()
  for (i in 1:length(d$patient_id)){
    ny1 = new_york_criteria_1_low_back_pain[i]
    ny2 = new_york_criteria_2_lumbar_spine_motion[i]
    ny3 = new_york_criteria_3_chest_expansion[i]
    if("new_york_criteria_4a_xray_sacroiliitis_bilat" %in% colnames(d) & "new_york_criteria_4b_xray_sacroiliitis_unilat" %in% colnames(d)){
      ny4a = new_york_criteria_4a_xray_sacroiliitis_bilat[i]
      ny4b = new_york_criteria_4b_xray_sacroiliitis_unilat[i]
    }else if("new_york_criteria_4_sacroiilitis" %in% colnames(d)){
      ny4=new_york_criteria_4_sacroiilitis[i]
    }
    
    if(is.na(ny1)){
      ny1_noNA = 0
    }else{
      ny1_noNA = ny1
    }
    if(is.na(ny2)){
      ny2_noNA = 0
    }else{
      ny2_noNA = ny2
    }
    if(is.na(ny3)){
      ny3_noNA = 0
    }else{
      ny3_noNA = ny3
    }
    if("new_york_criteria_4a_xray_sacroiliitis_bilat" %in% colnames(d)){
      if(is.na(ny4a)){
        ny4a_noNA = 0
      }else{
        ny4a_noNA = ny4a
      }
    }
    if("new_york_criteria_4b_xray_sacroiliitis_unilat" %in% colnames(d)){
      if(is.na(ny4b)){
        ny4b_noNA = 0
      }else{
        ny4b_noNA = ny4b
      }
    }
    if("new_york_criteria_4_sacroiilitis" %in% colnames(d)){
      if(is.na(ny4)){
        ny4_noNA = 0
      }else{
        ny4_noNA = ny4
      }
    }
    if("new_york_criteria_4a_xray_sacroiliitis_bilat" %in% colnames(d) & "new_york_criteria_4b_xray_sacroiliitis_unilat" %in% colnames(d)){
      if((ny4a_noNA == 1 | ny4b_noNA == 1) & (ny1_noNA == 1 | ny2_noNA == 1 | ny3_noNA == 1)){
        # Only case we can return 1 is when we observe at least a 1 in ny4a or ny4b and in ny1-3
        newd = c(newd,1)
      }else{
        if((!is.na(ny4a) & !is.na(ny4b) & ny4a == 0 & ny4b == 0) | (!is.na(ny1) & !is.na(ny2) & !is.na(ny3) & ny1 == 0 & ny2 == 0 & ny3 == 0)){
          # All inputs need to be observed to return 0
          newd = c(newd,0)
        }else{
          # If not return 1 and one input is NA, return NA
          newd = c(newd,NA)
        }
      }
    }else if("new_york_criteria_4_sacroiilitis" %in% colnames(d)){
      if(ny4_noNA == 1 & (ny1_noNA == 1 | ny2_noNA == 1 | ny3_noNA == 1)){
        # Only case we can return 1 is when we observe at least a 1 in ny4a or ny4b and in ny1-3
        newd = c(newd,1)
      }else{
        if((!is.na(ny4) & ny4 == 0) | (!is.na(ny1) & !is.na(ny2) & !is.na(ny3) & ny1 == 0 & ny2 == 0 & ny3 == 0)){
          # All inputs need to be observed to return 0
          newd = c(newd,0)
        }else{
          # If not return 1 and one input is NA, return NA
          newd = c(newd,NA)
        }
      }
    }
  }
  d$new_york_criteria = newd
  return(d)
}

ab_to_4<-function(df){
  df$new_york_criteria_4_sacroiliitis<-NA
  df$new_york_criteria_4_sacroiliitis[(df$new_york_criteria_4a_xray_sacroiliitis_bilat==1 | df$new_york_criteria_4b_xray_sacroiliitis_unilat==1)]=1
  df$new_york_criteria_4_sacroiliitis[(df$new_york_criteria_4a_xray_sacroiliitis_bilat==0 & df$new_york_criteria_4b_xray_sacroiliitis_unilat==0)]=0
  df<-df[,!(colnames(df) %in% c("new_york_criteria_4a_xray_sacroiliitis_bilat","new_york_criteria_4b_xray_sacroiliitis_unilat"))]
  return(df)
}

drop_haq<-function(df){
  haq_drops<-colnames(df)[grep("haq[0-9]",colnames(df))]
  haq_drops<-append(haq_drops,colnames(df)[grep("haq_[0-9]",colnames(df))])
  df<-df[,!(colnames(df) %in% haq_drops)]
  return(df)
}

paperless<-function(df){
  paper<-colnames(df)[grep("_paper$",colnames(df))]
  df<-df[,!names(df) %in% paper]
  return(df)
}

write_to_files<-function(){
  nation=unique(patient_table$country)[1]
  
  root1="C:\\Users\\AAND0774\\Downloads\\"
  root2="data_"
  root3=paste0("_",Sys.Date(),".xlsx")
  name=paste0(root2,nation,root3)
  
  file=paste0(root1,name)
  
  sheets<-list("pat"=patient_table,"med"=treatment_table,"vis"=visit_table)
  
  write_xlsx(sheets,file)
}

basfi_rename<-function(d){
  names(d)[names(d)=="basfi_1"]="basfi_1_socks"
  names(d)[names(d)=="basfi_2"]="basfi_2_pen"
  names(d)[names(d)=="basfi_3"]="basfi_3_shelf"
  names(d)[names(d)=="basfi_4"]="basfi_4_chair"
  names(d)[names(d)=="basfi_5"]="basfi_5_floor"
  names(d)[names(d)=="basfi_6"]="basfi_6_standing"
  names(d)[names(d)=="basfi_7"]="basfi_7_steps"
  names(d)[names(d)=="basfi_8"]="basfi_8_shoulder"
  names(d)[names(d)=="basfi_9"]="basfi_9_activities_demanding"
  names(d)[names(d)=="basfi_10"]="basfi_10_activities_day"
  return(d)
}

to_pat_map<-function(df,var1,var2,pat=patient_table){
  patients=df$patient_id
  pat[,col<-var1]=NA
  
  for(x in patients){
    temp=as.vector(as.matrix(unique(df[df$patient_id==x,col<-var2])))
    if(1 %in% temp | TRUE %in% temp){
      pat[pat$patient_id==x,col<-var1]<-1
    }else if(0 %in% temp | FALSE %in% temp){
      pat[pat$patient_id==x,col<-var1]<-0
    }
  }
  return(pat)
}

binarize<-function(d){
  for(x in colnames(d)){
    if("TRUE" %in% d[[x]] | "FALSE" %in% d[[x]]){
      d[d[,col<-x]=="TRUE",col<-x]=1
      d[d[,col<-x]=="FALSE",col<-x]=0
      d[[x]]=as.integer(d[[x]])
    }
  }
  return(d)
}

reverse_binary<-function(var){
  var[var==1]<-"A"
  var[var==0]<-"B"
  var[var=="A"]<-0
  var[var=="B"]<-1
  return(as.integer(var))
}

calculator_MASES_score <- function(
    d,
    costochondral_1st_joint_right = "costochondral_1st_joint_right",
    costochondral_1st_joint_left = "costochondral_1st_joint_left",
    costochondral_7th_joint_right = "costochondral_7th_joint_right",
    costochondral_7th_joint_left = "costochondral_7th_joint_left",
    post_sup_iliac_spine_right = "post_sup_iliac_spine_right",
    post_sup_iliac_spine_left = "post_sup_iliac_spine_left",
    iliac_crests_right = "iliac_crests_right",
    iliac_crests_left = "iliac_crests_left",
    ant_sup_iliac_spine_right = "ant_sup_iliac_spine_right",
    ant_sup_iliac_spine_left = "ant_sup_iliac_spine_left",
    achilles_tendon_insertion_right = "achilles_tendon_insertion_right",
    achilles_tendon_insertion_left = "achilles_tendon_insertion_left",
    lumbar_spinous_process_nr_5 = "lumbar_spinous_process_nr_5"
) {
  
  #if(is.null(d[[costochondral_1st_joint_right]])){stop("EROOR: variable does not exist!!")}
  #if(is.null(d[[costochondral_1st_joint_left]])){stop("EROOR: variable does not exist!!")}
  #if(is.null(d[[costochondral_1st_joint_right]])){stop("EROOR: variable does not exist!!")}
  #if(is.null(d[[costochondral_1st_joint_left]])){stop("EROOR: variable does not exist!!")}
  
  
  
  #check items exist (vi returnerer NA hvis et input mangler)
  if(sum(!is.na(d[[costochondral_1st_joint_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[costochondral_1st_joint_left]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[costochondral_7th_joint_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[costochondral_7th_joint_left]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[post_sup_iliac_spine_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[post_sup_iliac_spine_left]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[iliac_crests_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[iliac_crests_left]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[ant_sup_iliac_spine_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[ant_sup_iliac_spine_left]]))== 0){return(rep(times=nrow(d),NA))} 
  if(sum(!is.na(d[[achilles_tendon_insertion_right]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[achilles_tendon_insertion_left]]))== 0){return(rep(times=nrow(d),NA))}
  if(sum(!is.na(d[[lumbar_spinous_process_nr_5]]))== 0){return(rep(times=nrow(d),NA))}
  
  
  #calculate
  MASES_score_out <- d[[costochondral_1st_joint_right]] + d[[costochondral_1st_joint_left]] + 
    d[[costochondral_7th_joint_right]] + d[[costochondral_7th_joint_left]] + 
    d[[post_sup_iliac_spine_right]] + d[[post_sup_iliac_spine_left]] + 
    d[[iliac_crests_right]] + d[[iliac_crests_left]] + 
    d[[ant_sup_iliac_spine_right]] + d[[ant_sup_iliac_spine_left]] +
    d[[achilles_tendon_insertion_right]] + d[[achilles_tendon_insertion_left]] + 
    d[[lumbar_spinous_process_nr_5]]
  
  #return values
  return(MASES_score_out)
  
}

caspar_a1_calculator<-function(patient_table=patient_table,visit_table=visit_table){
  patient_table$caspar_criteria_1a_psoriasis_current=NA
  temp1<-unique(na.omit(visit_table[visit_table$comorb_psoriasis==1,]$patient_id))
  temp0<-unique(na.omit(visit_table[visit_table$comorb_psoriasis==0,]$patient_id))
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_1a_psoriasis_current=0
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_1a_psoriasis_current=1
  
  return(patient_table)
}

caspar_2_calculator<-function(patient_table=patient_table,visit_table=visit_table){
  patient_table$caspar_criteria_2_nail_symptoms=NA
  temp1<-unique(na.omit(visit_table[visit_table$nail_involvement %in% c("Mild","Moderate","Severe"),]$patient_id))
  temp0<-unique(na.omit(visit_table[visit_table$nail_involvement %in% c("None"),]$patient_id))
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_2_nail_symptoms=0
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_2_nail_symptoms=1
  
  return(patient_table)
}

caspar_3_calculator<-function(patient_table=patient_table,visit_table=visit_table){
  patient_table$caspar_criteria_3_igmrf_neg=NA
  temp1<-unique(na.omit(visit_table[visit_table$seropositivity==0,]$patient_id))
  temp0<-unique(na.omit(visit_table[visit_table$seropositivity==1,]$patient_id))
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_3_igmrf_neg=0
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_3_igmrf_neg=1
  
  return(patient_table)
}

caspar_4_calculator<-function(patient_table=patient_table,visit_table=visit_table){
  patient_table$caspar_criteria_4_dactylitis=NA
  temp1<-unique(na.omit(visit_table[visit_table$dactylitis==1,]$patient_id))
  temp0<-unique(na.omit(visit_table[visit_table$dactylitis==0,]$patient_id))
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_4_dactylitis=0
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_4_dactylitis=1
  
  return(patient_table)
}

caspar_5_calculator<-function(patient_table=patient_table,visit_table){
  patient_table$caspar_criteria_5_xray_changes=NA
  temp1<-unique(na.omit(visit_table[visit_table$erosive_changes==1 | visit_table$osteoproductive_changes==1,]$patient_id))
  temp0<-unique(na.omit(visit_table[visit_table$erosive_changes==0 & visit_table$osteoproductive_changes==0,]$patient_id))
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_5_xray_changes=0
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_5_xray_changes=1
  
  return(patient_table)
}

asas_11_calculator<-function(patient_table=patient_table,visit_table){
  patient_table$asas_criteria_11_elevated_crp<-NA
  temp1=c()
  temp0=c()
  
  for(id in unique(visit_table$patient_id)){
    temp_df<-visit_table[visit_table$patient_id == id,]
    if(max(temp_df$crp,na.rm=TRUE)>=10){
      temp1=append(temp1,id)
    }else{
      temp0=append(temp0,id)
    }
  }
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$asas_criteria_11_elevated_crp=0
  patient_table[patient_table$patient_id %in% temp1,]$asas_criteria_11_elevated_crp=1
  
  return(patient_table)
}  

NY_3_calculator<-function(patient_table,visit_table){
  patient_table$new_york_criteria_3_chest_expansion<-NA
  temp1=c()
  temp0=c()
  
  for(id in unique(visit_table$patient_id)){
    temp_df<-visit_table[visit_table$patient_id == id,]
    if(max(temp_df$chest_expansion,na.rm=TRUE)>2.5){
      temp1=append(temp1,id)
    }else{
      temp0=append(temp0,id)
    }
  }
  
  # the sequence of the following is IMPORTANT!!!!
  patient_table[patient_table$patient_id %in% temp0,]$new_york_criteria_3_chest_expansion=0
  patient_table[patient_table$patient_id %in% temp1,]$new_york_criteria_3_chest_expansion=1
  
  return(patient_table)
}

date_formatting<-function(d){
  years=lapply(d,function(x){str_extract(x,"^[0-9]{4}")})
  days=lapply(d,function(x){str_extract(x,"[0-9]{2}$")})
  month=gsub("^[0-9]{4}","",d)
  month=lapply(month,function(x){str_extract(x,"^[0-9]{2}")})
  d=paste0(days,month,years)
  d[d=="NANANA"]=NA
  return(d)
}

date_to_int<-function(d){
  if(any(nchar(d)<8) & !(any(grepl("-",d)))){
    d=as.Date(as.integer(d),origin="1899-12-30")
  }
  d=as.character(d)
  d=gsub("NA",NA,d)
  if(any(grepl("-",d))){
    d=lapply(d,function(x){paste(rev(str_split_fixed(x,"-",3)),collapse="")})
  }else if(unique(lapply(d,function(x){str_extract(x,"^[0-9]{4}")}) %in% as.character(c(1900:2023)))==TRUE){
    d=date_formating(d)
  }
  
  d=as.character(d)
  return(d)
}

caspar_calculator_v2 = function(d){
  newd = c()
  d_temp=d[,col<-c("row_id","patient_id")]
  
  d_temp$caspar_criteria=NA
  
  for (i in d_temp$row_id){
    d_id<-d[d$row_id==i,col<-grepl("caspar",colnames(d))]
    
    if(!(any(grepl("1a",colnames(d_id))))){
      d_id$caspar_1a=NA
    }
    if(!(any(grepl("1b",colnames(d_id))))){
      d_id$caspar_1b=NA
    }
    if(!(any(grepl("1c",colnames(d_id))))){
      d_id$caspar_1c=NA
    }
    if(!(any(grepl("2",colnames(d_id))))){
      d_id$caspar_2=NA
    }
    if(!(any(grepl("3",colnames(d_id))))){
      d_id$caspar_2=NA
    }
    if(!(any(grepl("4",colnames(d_id))))){
      d_id$caspar_4=NA
    }
    if(!(any(grepl("5",colnames(d_id))))){
      d_id$caspar_5=NA
    }
    
    d_1_id<-d_id[,col<-grepl("1",colnames(d_id))]
    D_id<-as.data.frame(d_id[,col<-grepl("[2-5]",colnames(d_id))])
    
    D_id$caspar_1=NA
    
    if(!(is.data.frame(class(d_1_id)))){
      d_1_id=as.data.frame(d_1_id)
    }
    if(!(is.data.frame(class(D_id)))){
      D_id=as.data.frame(D_id)
    }
    
    if(!(is.na(d_1_id[,col<-grepl("1a",colnames(d_1_id))])) && d_1_id[,col<-grepl("1a",colnames(d_1_id))]==1){
      D_id$caspar_1=2
    }else if(!(is.na(d_1_id[,col<-grepl("1b",colnames(d_1_id))])) && d_1_id[,col<-grepl("1b",colnames(d_1_id))]==1 | 
             !(is.na(d_1_id[,col<-grepl("1c",colnames(d_1_id))])) && d_1_id[,col<-grepl("1c",colnames(d_1_id))]==1){
      D_id$caspar_1=1
    }else if(!(all(is.na(d_1_id)))){
      D_id$caspar_1=0
    }
    
    D_sum=sum(D_id,na.rm=TRUE)
    D_NA=sum(is.na(D_id))
    
    
    if (D_sum > 2){
      d_temp$caspar_criteria[d_temp$row_id==i]=1
    }else{
      if ((is.na(D_id$caspar_1) && D_NA>2)|(D_NA>3)){
        d_temp$caspar_criteria[d_temp$row_id==i]=NA
      }else{
        d_temp$caspar_criteria[d_temp$row_id==i]=0
      }
    }
  }
  if("caspar_criteria" %in% colnames(d)){
    d=d[,!names(d) %in% c("caspar_criteria")]
  }
  d=merge(d,d_temp,by=c("row_id","patient_id"))
  
  return(d)
}

entheside_rename<-function(d){
  ent_names<-gsub("enthesides_body_","",colnames(d[grepl("enthesides_body_",colnames(d))]))
  names(d)[grepl("enthesides_body_",colnames(d))]<-ent_names
  names(d)[names(d)=="entire_anterior_superior_iliac_spine_left"]="ant_sup_iliac_spine_left"
  names(d)[names(d)=="entire_anterior_superior_iliac_spine_right"]="ant_sup_iliac_spine_right"
  names(d)[names(d)=="entire_iliac_crest_left"]="iliac_crests_left"
  names(d)[names(d)=="entire_iliac_crest_right"]="iliac_crests_right"
  names(d)[names(d)=="entire_posterior_superior_iliac_spine_left"]="post_sup_iliac_spine_left"
  names(d)[names(d)=="entire_posterior_superior_iliac_spine_right"]="post_sup_iliac_spine_right"
  names(d)[names(d)=="first_costochondral_junction_left"]="costochondral_1st_joint_left"
  names(d)[names(d)=="first_costochondral_junction_right"]="costochondral_1st_joint_right"
  names(d)[names(d)=="seventh_costochondral_junction_left"]="costochondral_7th_joint_left"
  names(d)[names(d)=="seventh_costochondral_junction_right"]="costochondral_7th_joint_right"
  names(d)[names(d)=="insertion_plantar_fascia_left"]="plantar_fascia_insertion_left"
  names(d)[names(d)=="insertion_plantar_fascia_right"]="plantar_fascia_insertion_right"
  names(d)[names(d)=="entire_spinous_process_of_fifth_lumbar_vertebra"]="lumbar_spinous_process_nr_5"
  return(d)
}

read_excel_v2<-function(text,sheetname=NULL){
  TEXT=read_excel(text,sheet=sheetname,col_types="text")
  TEXT[]<-lapply(TEXT,gsub, pattern="NA",replacement=NA,fixed=TRUE)
  TEXT[]<-lapply(TEXT,function(x){gsub("TRUE",as.integer(1),x)})
  TEXT[]<-lapply(TEXT,function(x){gsub("FALSE",as.integer(0),x)})
  for(x in colnames(TEXT)){
    # letters in variabel means that it is pure text
    if(any(grepl("[a-z,A-Z]",TEXT[[x]]))){
      TEXT[[x]]<-as.character(TEXT[[x]])
    # if there are no letters and there is a "." (or a "," between two digits for danish digit formats), it is numeric
    }else if(any(grepl("[.]",TEXT[[x]]))){
      TEXT[[x]]<-as.numeric(TEXT[[x]])
    }else if(any(grepl("\\d[,]\\d",TEXT[[x]]))){
      TEXT[[x]]<-as.numeric(gsub(",",".",TEXT[x]))
    # no letters nor "." means that it is either a date or an integer based on the column name
    }else if((!(grepl("date",x)) & any(grepl("[0-9]",TEXT[[x]])) ) | (x=="data_cut_date" & !(any(grepl("-",TEXT[[x]]))))){
      TEXT[[x]]<-as.integer(TEXT[[x]])
    }else if(x=="data_cut_date"){
      TEXT[[x]]<-date_to_int(TEXT[[x]])
    }else if(grepl("date",x)){
      if(any(grepl("-",TEXT[[x]]))){
        TEXT[[x]]=date_to_int(TEXT[[x]])
      }else{
        TEXT[[x]]<-as.integer(TEXT[[x]])
        if(any(nchar(TEXT[[x]])<8,na.rm=TRUE)){
          TEXT[[x]]<-as.Date(TEXT[[x]],origin="1899-12-30")
        }else if(all(nchar(TEXT[[x]])==8,na.rm=TRUE)){
          if(unique(lapply(as.character(TEXT[[x]]),function(d){str_extract(d,"^[0-9]{4}")}) %in% as.character(c(1900:2023)))==TRUE){
            TEXT[[x]]<-as.Date(as.character(TEXT[[x]]),format="%Y%m%d")
          }else{
            TEXT[[x]]<-as.Date(as.character(TEXT[[x]]),format="%d%m%Y")
          }
        }
        TEXT[[x]]=date_to_int(TEXT[[x]])
      }
    }else if(!(any(grepl("-",TEXT[[x]])))){
      TEXT[[x]]<-as.integer(TEXT[[x]])
    }
  }
  if(any(grepl("...",colnames(TEXT)))){
    drops=colnames(TEXT[grepl("[...]",colnames(TEXT))])
    for(x in drops){
      TEXT=TEXT[,!names(TEXT) %in% x]
    }
  }
  return(TEXT)
}

variables<-function(pat=NULL,med=NULL,vis=NULL){
  if(!(is.null(pat))){
    print("####### pat #######")
    print(sort(colnames(pat)))
  }
  if(!(is.null(med))){
    print("####### med #######")
    print(sort(colnames(med)))
  }
  if(!(is.null(vis))){
    print("####### vis #######")
    print(sort(colnames(vis)))
  }
}

basmi_average_calculator_v2<-function(d,new_name="basmi",var_pattern="basmi_",delete=FALSE,round_by=NULL){
  if(new_name %in% colnames(d)){
    d<-d[,!names(d) %in% new_name]
  }
  var=colnames(d[grepl(var_pattern,colnames(d))])
  temp=rep(0,nrow(d))
  for(x in var){
    temp=temp+as.numeric(d[[x]])
  }
  temp=temp/length(var)
  if(!(is.null(round_by)) && is.integer(round_by)){
    temp=round(temp,round_by)
  }
  if(delete){
    d<-d[,!names(d) %in% var]
  }
  d[[new_name]]<-temp
  return(d)
}

first_and_last_dates<-function(pat,vis){
  ids<-intersect(pat[["patient_id"]],vis[["patient_id"]])
  vis_temp=vis[,names(vis) %in% c("patient_id","visit_date")]
  vis_temp$visit_date=as.Date(vis_temp$visit_date,format="%d%m%Y")
  pat$date_of_first_visit=NA
  pat$date_of_last_visit=NA
  for(x in ids){
    pat$date_of_first_visit[pat$patient_id==x]=min(vis_temp$visit_date[pat$patient_id==x])
    pat$date_of_last_visit[pat$patient_id==x]=max(vis_temp$visit_date[pat$patient_id==x])
  }
  return(pat)
}


###################################################################
#main_file="C:/Users/AAND0774/Downloads/clinical_data_overview_files_20231010/data_CZ_2023-10-10.xlsx"

#patient_table = suppressWarnings(read_excel(main_file,sheet="pat"))
#treatment_table = suppressWarnings(read_excel(main_file,sheet="med"))
#visit_table = suppressWarnings(read_excel(main_file,sheet="vis"))


main_file="C:/Users/AAND0774/Downloads/OG_clinical_data/clinical_data_SL_20230815.xlsx"

patient_table = suppressWarnings(read_excel_v2(main_file,sheet="pat"))
treatment_table = suppressWarnings(read_excel_v2(main_file,sheet="med"))
visit_table = suppressWarnings(read_excel_v2(main_file,sheet="vis"))


