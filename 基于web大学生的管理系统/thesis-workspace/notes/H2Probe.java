import java.sql.*;
public class H2Probe {
  public static void main(String[] args) throws Exception {
    Class.forName("org.h2.Driver");
    String url = "jdbc:h2:file:./backend/data/volunteer;MODE=MySQL;DATABASE_TO_LOWER=TRUE;CASE_INSENSITIVE_IDENTIFIERS=TRUE";
    try (Connection c = DriverManager.getConnection(url, "sa", "")) {
      for (String sql : new String[]{
        "select id,username,role_code,ref_id,account_status from sys_user order by id",
        "select id,admin_no,name from admin_user order by id",
        "select id,student_no,name from student order by id"
      }) {
        System.out.println("SQL=" + sql);
        try (Statement s = c.createStatement(); ResultSet rs = s.executeQuery(sql)) {
          ResultSetMetaData md = rs.getMetaData();
          int cols = md.getColumnCount();
          while (rs.next()) {
            StringBuilder row = new StringBuilder();
            for (int i = 1; i <= cols; i++) {
              if (i > 1) row.append(" | ");
              row.append(rs.getString(i));
            }
            System.out.println(row);
          }
        }
      }
    }
  }
}