from infrastructure.persistence.base_entity import BaseEntity

class CoursesRepository(BaseEntity):
    def get_all_courses(self):
        query = "SELECT * FROM courses ORDER BY publication_date DESC"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_course(self, course_id):
        query = "SELECT * FROM courses WHERE uuid = %s"
        params = (str(course_id),)
        self.cursor.execute(query, params = params)
        return self.cursor.fetchall()
    
    def insert_couse(self, params_new_course):
        query = "INSERT INTO courses (uuid, title, description) VALUES (%s, %s, %s)"
        params = (str(params_new_course["uuid"]), params_new_course["title"], params_new_course["description"])
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return

    def delete_couse(self, course_id):
        query = "DELETE FROM courses WHERE uuid = %s"
        params = (str(course_id),)
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return
