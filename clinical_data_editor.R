source('~/GitHub/danbio.data.extraction.imaging/Denmark/functions/functions_old.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_basdai.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_basfi.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_MASES_score.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_asdas.R')
source('~/GitHub/danbio.data.extraction.imaging/Denmark/lib/calculator_criteria.R')
library(writexl)
library(stringr)

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
  haq_drops<-append(haq_drops,"haq_1_dress_yourself")
  df<-df[,!(colnames(df) %in% haq_drops)]
  return(df)
}

write_to_files<-function(){
  nation=unique(patient_table$country)[1]
  
  root1="C:\\Users\\AAND0774\\Downloads\\"
  root2="_data_"
  root3=paste0("_",Sys.Date(),".xlsx")
  name=paste0(root2,nation,root3)
  
  pat_file=paste0(root1,"pat",name)
  med_file=paste0(root1,"med",name)
  vis_file=paste0(root1,"vis",name)
  
  write_xlsx(patient_table,pat_file)
  write_xlsx(treatment_table,med_file)
  write_xlsx(visit_table,vis_file)
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
    d[d[,x]=="TRUE",x]=1
    d[d[,x]=="FALSE",x]=0
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
    post_sup_iliac_spine_right = "post_sup__iliac_spine_right",
    post_sup_iliac_spine_left = "post_sup__iliac_spine_left",
    iliac_crests_right = "iliac_crest_right",
    iliac_crests_left = "iliac_crest_left",
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
  temp1<-unique(visit_table[visit_table$comorb_psoriasis==1,]$patient_id)
  temp0<-unique(visit_table[visit_table$comorb_psoriasis==0,]$patient_id)
  
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_1a_psoriasis_current=1
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_1a_psoriasis_current=0
  
  return(patient_table)
}

caspar_5_calculator<-function(patient_table=patient_table,visit_table){
  patient_table$caspar_criteria_5_xray_changes=NA
  temp1<-unique(visit_table[1 %in% visit_table$erosive_changes | 1 %in% visit_table$osteoproductive_changes,]$patient_id)
  temp0<-unique(visit_table[!(1 %in% visit_table$erosive_changes | 1 %in% visit_table$osteoproductive_changes),]$patient_id)
  
  patient_table[patient_table$patient_id %in% temp1,]$caspar_criteria_5_xray_changes=1
  patient_table[patient_table$patient_id %in% temp0,]$caspar_criteria_5_xray_changes=0
  
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
  
  patient_table[patient_table$patient_id %in% temp1,]$asas_criteria_11_elevated_crp=1
  patient_table[patient_table$patient_id %in% temp0,]$asas_criteria_11_elevated_crp=0
  
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
  
  patient_table[patient_table$patient_id %in% temp1,]$new_york_criteria_3_chest_expansion=1
  patient_table[patient_table$patient_id %in% temp0,]$new_york_criteria_3_chest_expansion=0
  
  return(patient_table)
}

###################################################################
main_file="C:/Users/AAND0774/Downloads/clinical_data_overview_files_20231003/data_CZ_2023-10-03.xlsx"

patient_table = suppressWarnings(read_excel(main_file,sheet="pat"))
treatment_table = suppressWarnings(read_excel(main_file,sheet="med"))
visit_table = suppressWarnings(read_excel(main_file,sheet="vis"))



