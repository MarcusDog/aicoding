import java.sql.*;
public class H2ProbePwd {
  public static void main(String[] args) throws Exception {
    Class.forName("org.h2.Driver");
    String url = "jdbc:h2:file:./backend/data/volunteer;MODE=MySQL;DATABASE_TO_LOWER=TRUE;CASE_INSENSITIVE_IDENTIFIERS=TRUE";
    try (Connection c = DriverManager.getConnection(url, "sa", "")) {
      try (Statement s = c.createStatement(); ResultSet rs = s.executeQuery("select id,username,password_hash from sys_user order by id")) {
        while (rs.next()) {
          System.out.println(rs.getString(1) + " | " + rs.getString(2) + " | " + rs.getString(3));
        }
      }
    }
  }
}