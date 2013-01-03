/***	
 ***	avl.h --
 ***	
 ***	Definitions for the avl tree abstraction.
 ***	
 ***	N.Batchelder, 1/14/86.
 ***/

# ifndef avl_h
# define avl_h

/* 
 * These are the data structures which define an avl tree. 'Stuff' is
 * obviously just a place holder, since these functions can be used with any
 * type in the place of 'stuff'. The two functions provided work by having a
 * comparison function passed to them. This function gets things of type
 * 'stuff', and compares the parts that should be compared.
 */

typedef struct _avl	avl;
typedef int		stuff;
typedef int		keystuf;
typedef unsigned int	imap;

struct _avl {
	avl	*son[2];	/* The two subtrees */
	keystuf	ukey;		/* The user's key */
	stuff	udata;		/* The user's data */
	char	bal;		/* Index of higher son, 2 means equal */
};

# define NullTree	((avl *) 0)
# define NullKey	(0)
# define NullStuff	(0)
# define NoMore		((imap) -1)

/* 
 * Functions.
 */

imap	startiter(),
	nextnode();
int	addnode(),
	avlsize();
avl	*newavl();
	
# endif avl_h

/* end of avl.h */
