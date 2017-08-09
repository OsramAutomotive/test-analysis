<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">

  <html>
    <head>
      <link rel="stylesheet" type="text/css" href="styles.css"></link>
    </head>

    <body>
      <!-- Main Header -->
      <h2><div contenteditable="true">Test Tables</div></h2>
      
      <!-- Temperature Header -->
      <xsl:for-each select="test/temperature">
        <h2><div contenteditable="true"><xsl:value-of select="@temp"/></div></h2>
    
        <xsl:for-each select="mode">

          <table border="1">
            <!-- Mode Header -->
            <tr>
              <xsl:attribute name="class"><xsl:value-of select="@id"/></xsl:attribute>
              <th>
                <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                <div contenteditable="true"><xsl:value-of select="@id"/></div>
              </th>
            </tr>
            <xsl:for-each select="voltage">

              <!-- Voltage Header -->
              <tr bgcolor="#d3d3d3">
                <th>
                  <xsl:attribute name="colspan"><xsl:value-of select="@width"/></xsl:attribute>
                  <div contenteditable="true"><xsl:value-of select="@value"/></div>
                </th>
              </tr>

              <!-- Names -->
              <tr bgcolor="#d3d3d3">
                <th><div contenteditable="true">Name:</div></th>
                <xsl:for-each select="vsenses/vsense">
                  <td align="center"><div contenteditable="true"><xsl:value-of select="name"/></div></td>
                </xsl:for-each>
                <xsl:for-each select="systems/system">
                  <td align="center"><div contenteditable="true"><xsl:value-of select="name"/></div></td>
                </xsl:for-each>
              </tr>

              <!-- Minimums -->
              <tr>
                <th><div contenteditable="true">Min:</div></th>
                <xsl:for-each select="vsenses/vsense">
                  <td align="center"><xsl:value-of select="min"/></td>
                </xsl:for-each>
                <xsl:for-each select="systems/system">
                  <td align="center"><xsl:value-of select="min"/></td>
                </xsl:for-each>
              </tr>

              <!-- Maximums -->
              <tr>
                <th><div contenteditable="true">Max:</div></th>
                <xsl:for-each select="vsenses/vsense">
                  <td align="center"><xsl:value-of select="max"/></td>
                </xsl:for-each>
                <xsl:for-each select="systems/system">
                  <td align="center"><xsl:value-of select="max"/></td>
                </xsl:for-each>
              </tr>

              <!-- Check Data -->
              <tr>
                <th><div contenteditable="true">Check Data:</div></th>
                <xsl:for-each select="vsenses/vsense">
                  <xsl:choose>
                    <xsl:when test="check = 'Out of Spec'">
                      <td bgcolor="yellow" align="center"><xsl:value-of select="check"/></td>
                    </xsl:when>
                    <xsl:otherwise>
                      <td align="center"><xsl:value-of select="check"/></td>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:for-each>
                <xsl:for-each select="systems/system">
                  <xsl:choose>
                    <xsl:when test="check = 'Out of Spec'">
                      <td bgcolor="yellow" align="center"><xsl:value-of select="check"/></td>
                    </xsl:when>
                    <xsl:otherwise>
                      <td align="center"><xsl:value-of select="check"/></td>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:for-each>
              </tr>

            </xsl:for-each>
          </table>
          <br></br><br></br>

        </xsl:for-each><!-- end mode -->
        <br></br><br></br><br></br><br></br>
      </xsl:for-each><!-- end temperature -->
    </body>
  </html>

</xsl:template>
</xsl:stylesheet>