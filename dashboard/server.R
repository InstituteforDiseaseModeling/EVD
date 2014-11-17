# server.R
library(devtools)
library(ggplot2)
library(reshape2)
library(RCurl)      
library(data.table)
library(maptools)

shinyServer(function(input, output) {
  getVarHeight <- function() {
    print(length(input$country)*800)
    return(length(input$country) * 800)
  }
#   output$text <- renderText({
#     for (i in input$country)
#     {
#       print(h4(i))
#     }
#   output$map <- renderPlot({
#     countrylist=c("sierra_leone","guinee","liberia")
#     for (i in input$country)
#     {
#       filelocation <- paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/",countrylist[strtoi(i)], "_shapefile.csv",sep="")
#       download.file(filelocation, "district.shp")
#       shapes<-readShapeSpatial("district.shp",
#                              proj4string=CRS("+proj=longlat"))
#     }
#   })
  output$plots <- renderPlot({
    countrylist=c("Sierra_Leone","Guinea","Liberia")
    countrylist2=c("sierra_leone","guinee","liberia")
    countryname=c("Sierra Leone", "Guinea", "Liberia")
    countrykey=c("557dba7yrzgumhq","32gsxuvpea9eix3","bpyiscdre1vlg3f")
    casefinal <- NA
    for (i in input$country)
    {
      #file1 <- getURL(paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/data/",countrylist2[strtoi(i)], "_EVD_2014.csv",sep=""), ssl.verifypeer = FALSE)
      file1 <- getURL(paste("https://dl.dropboxusercontent.com/s/",countrykey[strtoi(i)], "/case_reports_",countrylist[strtoi(i)], ".csv?dl=1",sep=""), ssl.verifypeer = FALSE)
      case1 <- read.csv(text = file1, stringsAsFactors = F)
      case1$X <- as.Date(case1$X, format="%m/%d/%Y")
      filepop <- getURL(paste("https://raw.githubusercontent.com/InstituteforDiseaseModeling/EVD/master/data/",countrylist2[strtoi(i)], "_population.csv",sep=""), ssl.verifypeer = FALSE)
      pop <- read.csv(text = filepop, stringsAsFactors = F)
      pop <- as.data.table(pop)
      
      idx=1
      for (colname in colnames(case1))
      {
        newcolname <- paste(colname, ",", countryname[strtoi(i)], sep="")
        #popcount <- pop[district==colname,pop]
        #if (length(popcount)>0)
        #{
          #popcount <- round(popcount / 1000,0)
          #newcolname <- paste(colname, ",", countryname[strtoi(i)], sep="")
          #newcolname <- paste(colname, ",", countryname[strtoi(i)],"\n", "pop=",popcount, "K", sep="")
          #colnames(case1)[idx] <- newcolname
        #}
        idx=idx+1
      }

    if (is.na(casefinal))
    {
      casefinal <- case1
    }
    else
    {
      casefinal <- merge(casefinal, case1, by="X")
    }
    }
    casefinal$Week <- week(casefinal$X)
    casefinal$Month <- month(casefinal$X)
    casefinal <- as.data.table(casefinal)
    
    if (input$aggregation==2)
    {
      casefinal <- casefinal[,lapply(.SD,sum,na.rm=TRUE),by = Week]
      casefinal$X <- as.POSIXct(paste("2014",casefinal$Week,"1"), format="%Y %U %u")
    }
    else if (input$aggregation==3)
    {
      casefinal <- casefinal[,lapply(.SD,sum,na.rm=TRUE),by = Month]
      casefinal$X <- as.POSIXct(paste("2014",casefinal$Month,"1"), format="%Y %m %d")
    }
    casefinal$Week <- NULL
    casefinal$Month <- NULL
    casefinal$Total <- rowSums(subset(casefinal,select=-X),na.rm=TRUE)
    
    p <- ggplot(melt(casefinal, id.vars="X"),aes(x=X,y=value))+
      geom_point(size = 1)+geom_line()+facet_wrap(~ variable,ncol = 4,scales = "free") +
      xlab("Time") +
      ylab("Number of New Cases") + theme_bw()
    if (input$yscale==2)
      {
        p <- p + scale_y_log10()
      }
    p
  }, width=1000, height=getVarHeight) 
  }
  )