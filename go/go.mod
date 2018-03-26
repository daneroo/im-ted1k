module "github.com/daneroo/im-ted1k/go"

// actual time: 2015-11-13T21:30:10Z
require (
	// mysql is actually v1.3 but I pinned it because of bug in vgo
	// ( it builds only the first time, perhaps because of no patch in the version)
	"github.com/go-sql-driver/mysql" v0.0.0-20161201115036-a0583e0143b1
	"github.com/mattn/go-sqlite3" v1.6.0
	// actual time: 2015-11-13T21:30:10Z
	"github.com/tarm/serial" v0.0.0-20151113213010-edb665337295
)
