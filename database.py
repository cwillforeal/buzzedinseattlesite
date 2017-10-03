import sqlalchemy
from sqlalchemy import Table,Column,String,Text,LargeBinary
from sqlalchemy.orm import sessionmaker

#Setup the connect parameters to database
POSTGRES = {
    'user': 'buzzedinseattle',
    'pw': 'Amy123',
    'db': 'buzzedinseattle',
    'host': 'localhost',
    'port': '5432',
}
url_postgres = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

class Database():
    def __init__(self):
        #Connect to the database, currently using default settings
        self.con = sqlalchemy.create_engine(url_postgres, client_encoding='utf8')

        #Bind the connection ot MetaData()
        self.meta = sqlalchemy.MetaData(bind=self.con, reflect=True)

        #Get a session going
        Session = sessionmaker()
        Session.configure(bind=self.con)
        self.session = Session() 

    def addPost(self, title, description, image):
        if 'blog_posts' not in self.meta.tables:
            post = Table('blog_posts', self.meta,
                Column('title', String(140), unique=True),
                Column('description', Text),
                Column('image', LargeBinary))

            self.meta.create_all(self.con) 
        else:
            post = self.meta.tables['blog_posts']

        #Write the values to the table 
        post_insert = post.insert().values(title = title, description = description, image = image)
        #Execute the write
        self.con.execute(post_insert)

    def findPost(self,title):
        if 'blog_posts' not in self.meta.tables:
            return None

        posts = self.meta.tables['blog_posts']
        row = self.session.query(posts).filter(posts.c.title == title).first()
        return row

    def editPost(self,title,title_edit,description_edit,image_edit):
        if 'blog_posts' not in self.meta.tables:
            return None

        posts = self.meta.tables['blog_posts']

        if not image_edit.filename == "":
            update = posts.update().where(posts.c.title == title).values(title = title_edit, description = description_edit, image = image_edit.read())
        else:
            update = posts.update().where(posts.c.title == title).values(title = title_edit, description = description_edit)

        if update == None:
            return False

        self.con.execute(update)
        return True

    def deletePost(self, title):
        if 'blog_posts' not in self.meta.tables:
            return None

        posts = self.meta.tables['blog_posts']
        delete = posts.delete().where(posts.c.title == title)
        self.con.execute(delete)
        return True

    def getAllPosts(self):
        if 'blog_posts' not in self.meta.tables:
            return None

        posts = self.meta.tables['blog_posts']
        select_all = posts.select()
        return self.con.execute(select_all)

