(function (models,collection){
  app.models.Post=Backbone.Model.extend({
        defaults:{ 
            title:"",
            body:"body of post",
            date:"date of the post",
            updated:""
            
          
        },

        initialize: function() {
	      
			if (!this.get("title")) {
				this.set({"title": this.defaults.title});
			}
		},
        url:function(){
                    console.log(app.Posts.url);
            if ((this.id=="") || (typeof this.id=="undefined")) {
               
                return app.Posts.url;
            }
            else {//collection ==a model
           //    if (app.Posts.length==1)
             //       return app.Posts.url
                if (app.Posts.url.split('/').length===3)
                    return  app.Posts.url;
		else
		    return  app.Posts.url+"/"+this.id;
	
            }
            
        }
        
    });
  
})(app.models);